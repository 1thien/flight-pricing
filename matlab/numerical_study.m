%NUMERICAL_STUDY Convergence, Monte Carlo and interpolation checks for the DP.
%   Reads study_input.mat (jump-model parameters lam, mu, kappa, sigma as
%   1 x 61 vectors, fit on all departed trips) and writes study_output.mat.
%
%   1. Grid convergence: solve on grids of K = 25..1600 points and track
%      V_60(0), the expected price paid starting 60 days out at the route's
%      usual fare, and the day-30 buy threshold.
%   2. Monte Carlo: simulate the continuous jump process under the finest
%      grid's policy and compare the average price paid with V_60(0).
%   3. Interpolation: linear vs. pchip between grid points for the policy.

in = load('study_input.mat');
lam = in.lam(:)'; mu = in.mu(:)'; kappa = in.kappa(:)'; sigma = in.sigma(:)';
x_min = -1.0; x_max = 1.5;

% 1. Grid convergence --------------------------------------------------------
Ks = [25 50 100 200 400 800 1600];
v60 = zeros(size(Ks)); b30 = zeros(size(Ks)); runtime = zeros(size(Ks));
for k = 1:numel(Ks)
    tic;
    edges = linspace(x_min, x_max, Ks(k) + 1);
    centers = (edges(1:end-1) + edges(2:end)) / 2;
    M = jump_transitions(edges, lam, mu, kappa, sigma);
    [V, C] = backward_induction(M, centers);
    v60(k) = interp1(centers, V(:, 61), 0, 'linear');
    buy = exp(centers(:)) <= C(:, 31);           % 30 days left is column 31
    b30(k) = max([centers(buy), -inf]);          % highest relative fare still worth buying
    runtime(k) = toc;
end
diffs = abs(diff(v60));
order = log2(diffs(1:end-1) ./ diffs(2:end));    % observed order of convergence

% Keep the finest solution for the policy below.
V_fine = V; C_fine = C; centers_fine = centers;

% 2. Monte Carlo -------------------------------------------------------------
rand('seed', 1); randn('seed', 1);   % works in MATLAB and Octave
Ns = [1e2 1e3 1e4 1e5 1e6];
mc_mean = zeros(size(Ns)); mc_se = zeros(size(Ns));
for k = 1:numel(Ns)
    N = Ns(k);
    x = zeros(N, 1); paid = nan(N, 1); waiting = true(N, 1);
    for t = 61:-1:2
        cont = interp1(centers_fine, C_fine(:, t), min(max(x, centers_fine(1)), centers_fine(end)), 'linear');
        buy_now = waiting & (exp(x) <= cont);
        paid(buy_now) = exp(x(buy_now));
        waiting = waiting & ~buy_now;
        jump = rand(N, 1) < lam(t);
        J = mu(t) + kappa(t) * x + sigma(t) * randn(N, 1);
        x = x + jump .* J;
        x = min(max(x, x_min), x_max);
    end
    paid(waiting) = exp(x(waiting));                 % last day: must buy
    mc_mean(k) = mean(paid);
    mc_se(k) = std(paid) / sqrt(N);
end
mc_error = abs(mc_mean - v60(end));

% 3. Interpolation ------------------------------------------------------------
% Compare the buy threshold read off a coarse grid (K = 50) with linear vs.
% pchip interpolation of the continuation value, against the fine-grid answer.
edges_c = linspace(x_min, x_max, 51);
centers_c = (edges_c(1:end-1) + edges_c(2:end)) / 2;
[~, C_c] = backward_induction(jump_transitions(edges_c, lam, mu, kappa, sigma), centers_c);
xq = linspace(-0.6, 0.6, 2001);
interp_err = zeros(2, 60);
for t = 2:61
    ref = exp(xq) <= interp1(centers_fine, C_fine(:, t), xq, 'linear');
    lin = exp(xq) <= interp1(centers_c, C_c(:, t), xq, 'linear');
    pch = exp(xq) <= interp1(centers_c, C_c(:, t), xq, 'pchip');
    interp_err(1, t - 1) = mean(lin ~= ref);
    interp_err(2, t - 1) = mean(pch ~= ref);
end

% 4. Real options: value of the right to wait, at the usual fare -------------
option_value = 1 - interp1(centers_fine, V_fine, 0, 'linear');   % 1 x 61, by days left
thresholds = zeros(1, 61);
for t = 2:61
    buy = exp(centers_fine(:)) <= C_fine(:, t);
    thresholds(t) = max([centers_fine(buy), -inf]);
end

save('-v7', 'study_output.mat', 'Ks', 'v60', 'b30', 'runtime', 'diffs', 'order', ...
     'Ns', 'mc_mean', 'mc_se', 'mc_error', 'interp_err', 'option_value', 'thresholds');
fprintf('V60(0) by grid: %s\n', mat2str(v60, 6));
fprintf('observed order: %s\n', mat2str(order, 3));
fprintf('Monte Carlo error: %s\n', mat2str(mc_error, 3));
