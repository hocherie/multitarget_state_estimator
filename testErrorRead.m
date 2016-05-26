% Reads shark mean position estimate log file from att_line_pf.py and
% plots

% 
% % % Read File
% M = csvread('catalina_error.txt');
% 
% x = M; % Error of shark's distance from line
% 
% plot(x', '.');
% xlabel('Time (s)');
% ylabel('y distance from att (m)')
% title('Error in Distance From Line')
% 
% % Plot Mean
% x = mean(x);
% figure
% plot(x', '.')
% title('Mean Error in Distance From Line')


% % Read File (est and actual)
M = csvread('catalina_error.txt');
est_50 = M(:,1:2:end); % Est Error of shark's distance from line
act_50 = M(:,2:2:end); % Act Error of shark's distance from line

hold on
plot(est_50', '.');
plot(act_50', '-');
hold off

xlabel('Time (s)');
ylabel('y distance from att (m)')
title('Error in Distance From Line')

% Plot Mean
est_mean_50 = mean(est_50);
act_mean_50 = mean(act_50);
figure
hold on
plot(est_mean_50', '.')
plot(act_mean_50', '-')
legend('Est', 'Act')
title('Mean Error in Distance From Line')
% 