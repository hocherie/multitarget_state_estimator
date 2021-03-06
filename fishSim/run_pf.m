% Script to Run Particle Filter and Graphs Resulting Performance
clf

% Preallocate Lists
N_trial = 2;
tag_list = 50;
ts_pf = 100;
N_fish = 50;
seg_length = 20;

% Preallocate List
tag_list_size = size(tag_list, 2);
act_error_list = zeros(ts_pf, 1);
est_error_list = zeros(ts_pf, tag_list_size);
error_list = zeros(ts_pf, tag_list_size);
numshark_est_list = zeros(ts_pf, tag_list_size);
error_list = zeros(ts_pf, tag_list_size);
seglen_list = zeros(ts_pf, tag_list_size);
tagrange_list = zeros(ts_pf, tag_list_size);
seglendist_list = zeros(ts_pf, tag_list_size);
d90_list_est = zeros(ts_pf, tag_list_size);
d90_list_act = zeros(ts_pf, tag_list_size);

for i = 1:tag_list_size
    
    act_error_tag = zeros(ts_pf, N_trial);
    est_error_tag = zeros(ts_pf, N_trial);
    error_tag = zeros(ts_pf, N_trial);
    numshark_est_tag = zeros(ts_pf, N_trial);
    seglen_est_tag = zeros(ts_pf, N_trial);
    tagrange = zeros(ts_pf, N_trial);
    seglendist_est_tag = zeros(ts_pf, N_trial);
    d90_est_tag = zeros(ts_pf, N_trial);
    d90_act_tag = zeros(ts_pf, N_trial);
    
    N_tag = tag_list(i);
    
    for j = 1:N_trial
        
        [x,y,t] = fishSim_7(N_fish,seg_length, 1e3, 1e6, 1e9);
        LINE_START = [-seg_length/2 0];
        LINE_END = [seg_length/2 0];
        [act_error, est_error, error, numshark_est, x_robots, y_robots, numtag_range, seg_len_est, d90_est, d90_act,seg_len_dist_est] ...
            = att_pf(x, y, t, N_tag, LINE_START, LINE_END, ts_pf, false);
        
        % Assign to lists
        size(act_error)
        act_error_tag(:,j) = act_error;
        est_error_tag(:,j) = est_error;
        error_tag(:,j) = error;
        numshark_est_tag(:,j) = numshark_est;
        seglen_est_tag(:,j) = seg_len_est;
        seglendist_est_tag(:,j) = seg_len_dist_est;
        d90_est_tag(:,j) = d90_est;
        d90_act_tag(:,j) = d90_act;
    end
       
    % Average Across Trials
    act_error_list(:,i) = mean(act_error_tag,2);
    est_error_list(:,i) = mean(est_error_tag,2);
    error_list(:,i) = mean(error_tag, 2);
    numshark_est_list(:,i) = mean(numshark_est, 2);
    seglen_list(:,i) = mean(seglen_est_tag, 2);
end

save('pf_line.mat', 'act_error_list', 'est_error_list', 'error_list','numshark_est_list',...
    'ts_pf','N_fish','tag_list','seglen_list', 'd90_list_est', 'd90_list_act','seg_length','seglendist_list')
