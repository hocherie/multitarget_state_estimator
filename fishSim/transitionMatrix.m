% Generate Transition Matrix Based on Simulation Data
% States are distance away from line
% Structure based on Kevin Smith's code



% Discretize location to node number

%% For Simulation Data
% ts_len = length(x); % Number of ts
% ns = size(x,2);
% dist = zeros(ts_len, ns);
% 
% for i = 1:ts_len
%     for j = 1:ns
% %         is_above = isAbove(x(i,j), y(i,j), [-25 0], [25 0]);
% %         dist(i,j) = is_above * point_to_line(x(i,j), y(i,j), [-25 0], [25 0]);
%         dist(i,j) = y(i,j);
%     end
% end

%% For Actual Data
ts_len = length(x_sharks); % Number of ts
ns = size(x_sharks,2);
dist = zeros(ts_len, ns);
dist = distLine;
% 
max_dist = max(abs(dist(:)))
max_dist = 7;
edges = -max_dist:0.25:max_dist; % Create hist bin edges
N = length(edges);
Y_node = discretize(dist,edges); % Location to discretized index

%% Compute transition matrix (only for one shark)
T = zeros(N, N);

for ts = 1 : ts_len - 1
    for shark = 1:ns
        old_node = Y_node(ts, shark);
        new_node = Y_node(ts+1, shark);
        T(new_node, old_node) = T(new_node, old_node) + 1;
    end
end

% Normalize transition matrix

for from = 1:N
    sum_from = sum(T(:,from));
    T(:,from) = T(:,from)/sum(T(:,from));
    
    if sum_from == 0
        T(:,from) = zeros([1 N]);
    end
    
end

