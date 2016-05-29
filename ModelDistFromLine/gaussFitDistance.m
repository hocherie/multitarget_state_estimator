clf 
muhat_list = zeros(10,1)
sigmahat_list = zeros(10,1)

for i = 1:15
    string = strcat(num2str(i*10), 'SharksDistFromLine.txt');
    M = csvread(string, 2, 0);
    sum_dist = sum(M,2);
    B = reshape(sum_dist, 1, []);
    % Replicate to negative distances
    B = [-B, B];
    h = histogram(B);
    [muhat, sigmahat] = normfit(B);
    muhat_list(i) = muhat;
    sigmahat_list(i)= sigmahat;
end



num_sharks = linspace(10,150,15)';


plot(num_sharks, sigmahat_list, 'x')

linear_coe = polyfit(num_sharks, sigmahat_list, 1);
xFit = linspace(0,150,1000)
yFit = polyval(linear_coe, xFit);
hold on
% lsline;
plot(xFit, yFit);
xlabel('Number of Sharks')
ylabel('Sigma from Gaussian Fit')
hold off