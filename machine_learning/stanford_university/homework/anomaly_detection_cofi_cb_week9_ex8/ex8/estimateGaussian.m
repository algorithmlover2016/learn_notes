function [mu sigma2] = estimateGaussian(X)
%ESTIMATEGAUSSIAN This function estimates the parameters of a 
%Gaussian distribution using the data in X
%   [mu sigma2] = estimateGaussian(X), 
%   The input X is the dataset with each n-dimensional data point in one row
%   The output is an n-dimensional vector mu, the mean of the data set
%   and the variances sigma^2, an n x 1 vector
% 

% Useful variables
[m, n] = size(X);

% You should return these values correctly
mu = zeros(n, 1);
sigma2 = zeros(n, 1);

% ====================== YOUR CODE HERE ======================
% Instructions: Compute the mean of the data and the variances
%               In particular, mu(i) should contain the mean of
%               the data for the i-th feature and sigma2(i)
%               should contain variance of the i-th feature.
%
% reference to https://blog.csdn.net/qq_35564813/article/details/79831616
mu = mean(X, 1)'; % mu = mean(X', 2); % mu = sum(X) / m;

muExt = mu(:, ones(1, m))';

sigma2 = sum((X - muExt) .^ 2, 1)' / m; % sigma2 = sum((X - mu) .^ 2) / m;







% =============================================================


end
