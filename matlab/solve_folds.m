%SOLVE_FOLDS Backward induction for each walk-forward fold.
%   Reads dp_input.mat from the current folder:
%     edges (1 x K+1), centers (1 x K)
%     M_markov (K x K x 61 x nfolds)       empirical transition matrices
%     lam, mu, kappa, sigma (61 x nfolds)  jump-model parameters
%   Writes dp_output.mat with continuation values C_<model>_<objective>
%   (K x 61 x nfolds) for model in {markov, jump} and objective in
%   {price, log}.

in = load('dp_input.mat');
nf = size(in.lam, 2);
K = numel(in.centers);
objectives = {'price', 'log'};
out = struct();
for o = 1:2
    obj = objectives{o};
    Cm = zeros(K, 61, nf); Cj = Cm;
    for f = 1:nf
        [~, C] = backward_induction(in.M_markov(:, :, :, f), in.centers, obj);
        Cm(:, :, f) = C;
        Mj = jump_transitions(in.edges, in.lam(:, f)', in.mu(:, f)', in.kappa(:, f)', in.sigma(:, f)');
        [~, C] = backward_induction(Mj, in.centers, obj);
        Cj(:, :, f) = C;
    end
    out.(['C_markov_' obj]) = Cm;
    out.(['C_jump_' obj]) = Cj;
end
save('-v7', 'dp_output.mat', '-struct', 'out');
fprintf('solved %d folds x 2 models x 2 objectives on a %d-point grid\n', nf, K);
