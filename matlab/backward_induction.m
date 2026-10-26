function [V, C] = backward_induction(M, centers, objective)
%BACKWARD_INDUCTION Solve the buy-or-wait Bellman equation on a price grid.
%   Column c of every array stands for day d = c - 1 (days before departure),
%   so day 1, the last chance to buy, is column 2. Column 1 is unused.
%
%   M(i, j, c) is the probability of moving from grid point i on day c-1 to
%   grid point j on day c-2. centers are the relative log fares x.
%
%   objective chooses what "cost" means at grid point i:
%     'price' (default): exp(x_i), the fare in units of the route's usual fare.
%                        Minimizing it minimizes expected dollars paid.
%     'log':             x_i, the log fare. Differences in log fare are
%                        roughly percentages, so this minimizes expected
%                        % paid, treating every trip equally.
%
%   V(:, 2) = cost                            last day: must buy
%   C(:, c) = M(:, :, c) * V(:, c-1)          expected cost of waiting a day
%   V(:, c) = min(cost, C(:, c))              buy now or wait, whichever is cheaper
%
%   Works in MATLAB and GNU Octave.

    if nargin < 3, objective = 'price'; end
    if strcmp(objective, 'log')
        cost = centers(:);
    else
        cost = exp(centers(:));
    end
    K = numel(centers);
    T = size(M, 3);
    V = repmat(cost, 1, T);
    C = inf(K, T);              % no waiting on day 1 (column 2) or before
    for c = 3:T
        C(:, c) = M(:, :, c) * V(:, c - 1);
        V(:, c) = min(cost, C(:, c));
    end
end
