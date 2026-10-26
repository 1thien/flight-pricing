function M = jump_transitions(edges, lam, mu, kappa, sigma)
%JUMP_TRANSITIONS Discretize the jump model onto a grid.
%   With t days left the relative log fare x either stays put (probability
%   1 - lam(t)) or jumps by J ~ Normal(mu(t) + kappa(t)*x, sigma(t)^2).
%   Each grid point i is represented by its bin center; probability mass
%   that lands outside the grid is assigned to the end bins.
%
%   Uses erfc for the normal CDF so it runs without the Statistics Toolbox
%   and in GNU Octave.

    K = numel(edges) - 1;
    T = numel(lam);
    centers = (edges(1:end-1) + edges(2:end)) / 2;
    Phi = @(z) 0.5 * erfc(-z / sqrt(2));
    M = zeros(K, K, T);
    inner = edges(2:end-1);
    for t = 2:T
        if isnan(lam(t)), continue; end
        for i = 1:K
            m = centers(i) + mu(t) + kappa(t) * centers(i);   % mean of x tomorrow, given a jump
            cdf = Phi((inner - m) / sigma(t));
            p = diff([0, cdf, 1]);                             % mass in each bin, tails to end bins
            row = lam(t) * p;
            row(i) = row(i) + (1 - lam(t));                    % no jump: stay in place
            M(i, :, t) = row;
        end
    end
end
