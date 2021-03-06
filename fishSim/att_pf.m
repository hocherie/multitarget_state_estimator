function [act_error, est_error, error, numshark_est, x_robots, y_robots, num_tag_covered, seg_len, d90_est_list, d90_act_list, seg_len_dist] ...
    = att_pf(x, y, t, N_tagged, LINE_START, LINE_END, TS_PF, show_visualization)
% Particle filter to estimate attraction line and number of
% fish in the fish swarm

% PF Constants
Height = 10;
Width = 30;
N_part = 100;
Sigma_mean = 1;
N_fish = size(x,2);

% AUV Constants
N_robots = 10;
range = 100;

numshark_sd = 0.65;

randomSharks = randperm(N_fish, N_tagged); % Randomize Selection of Sharks
x_tagged = x(:, randomSharks);
y_tagged = y(:, randomSharks);

% Initialize States
robots = initRobots(50,N_robots);
p = initParticles(Height, Width, N_part);

est_error = zeros(TS_PF,1);
act_error = zeros(TS_PF,1);
error = zeros(TS_PF,1);
num_tag_covered = zeros(TS_PF,1);
numshark_est = zeros(TS_PF,1);
numshark_old = zeros(N_part, 2);
seg_len = zeros(TS_PF,1);
seg_len_dist = zeros(TS_PF,1);
d90_est_list = zeros(TS_PF,1);
d90_act_list = zeros(TS_PF,1);
shark_dist_cum_list = zeros(TS_PF,N_fish); % keeps track of all shark distance

x_robots = zeros(N_robots, TS_PF);
y_robots = zeros(N_robots, TS_PF);

x_tagged = x(:, randomSharks);
y_tagged = y(:, randomSharks);

estimated = mean(p); 


for i = 1:TS_PF
    % Find tagged shark in range of robot
    [i_range, x_range, y_range] = getNearbyTags(robots,range, x(i,:),y(i,:));
    N_inRange = size(i_range, 2);
    num_tag_covered(i) = N_inRange;
    
    % TODO: implement tag
    x_range = x_tagged(i,:);
    y_range = y_tagged(i,:);
    
    if ~mod(i, 100) % Display timestep periodically
        disp(i)
    end
    numshark_old(:,2) = numshark_old(:,1); % keep track of n-2
    numshark_old(:,1) = p(:,5);
    
    p = propagate(p, Sigma_mean, numshark_old(:,2), LINE_START, LINE_END);  
    w = getParticleWeights(p, x_range, y_range, shark_dist_cum_list(1:i-1,:), @fit_sumdist_sd, @fit_sumdist_mu, numshark_sd);
    p = resample(p,w);
    p_mean = computeParticleMean(p,w)
    current_points_to_line = points_to_line(x_range, y_range, [p_mean(1), p_mean(2)], [p_mean(3), p_mean(4)]);
    size(current_points_to_line)
    shark_dist_cum_list(i,:) = ... % Update cumulative shark distance list
        current_points_to_line;
    
    % TODO: Line Fit Correction
    line_error = zeros(size(x, 2), 1);
    for s=1:size(x, 2)
        line_error(s) = point_to_line(x(s), y(s), [p_mean(1), p_mean(2)],...
            [p_mean(3), p_mean(4)]);
    end

    Z_line = sum(line_error) % Sum of distance
    prob_line = normpdf(Z_line, 0, 200)
    
    % Calculate Segment Length
    seg_len(i) = dist(p_mean(1), p_mean(2), p_mean(3), p_mean(4));
%     max_area = max(abs(y(i,:))) * seg_len(i)

    
    % Move Robot
    robots = moveRobots(robots, x_range, y_range, ...
        [p_mean(1) p_mean(2)], [p_mean(3) p_mean(4)]);
    
    x_robots(:,i) = robots(:,1);
    y_robots(:,i) = robots(:,2);
    
    
    % Calculate Sum of Distance for actual and estimated line
    est_error(i) = totalSharkDistance(x(i,:), y(i,:), LINE_START, LINE_END);
    act_error(i) = totalSharkDistance(x(i,:), y(i,:), LINE_START, LINE_END);

    % Performance Error: Error between actual and estimated line
    error(i) = pfError(x(i,:), y(i,:), LINE_START, LINE_END, [p_mean(1), p_mean(2)], [p_mean(3), p_mean(4)], N_fish);
    numshark_est(i) = p_mean(5);
    
    % Segment Length
    seg_len(i) = dist(p_mean(1),p_mean(2),p_mean(3),p_mean(4));
    
    % Estimated Segment Length based on distance
    seg_len_dist_i = measureEdgeDistance(x(i,:),y(i,:),[p_mean(1),p_mean(2)],[p_mean(3),p_mean(4)]);
    seg_len_dist(i) = seg_len_dist_i;
    
    % d90_estimated (with PF estimated line)
    line_error_est = zeros(size(x, 2), 1);
    for s=1:size(x, 2)
        line_error_est(s) = point_to_line(x(i,s), y(i,s), [p_mean(1),p_mean(2)], [p_mean(3),p_mean(4)]);
    end
    d90_est_list(i) = prctile(line_error_est, 90);
    
    % d90_actual (with actual attraction line)
    line_error_act = zeros(size(x, 2), 1);
    for s=1:size(x, 2)
        line_error_act(s) = point_to_line(x(i,s), y(i,s), [LINE_START(1),LINE_START(2)], [LINE_END(1),LINE_END(2)]);
    end
    d90_act_list(i) = prctile(line_error_act, 90);

    % Visualize Sharks and Particles
        
    if show_visualization

        arrowSize = 1.5;
        fig = figure(1);
        clf;
        hold on;
        
        % Plot in range sharks
        for f = i_range
           plot(x(i,f),y(i,f),'x'); 
           plot([x(i,f) x(i,f)+cos(t(i,f))*arrowSize],[y(i,f) y(i,f)+sin(t(i,f))*arrowSize]); 
        end
       
        
%         % Plot Tagged Sharks
%         for f=1:N_tagged
%            plot(x_tagged(i,f),y_tagged(i,f),'x'); 
%            plot([x_tagged(i,f) x_tagged(i,f)+cos(t_tagged(i,f))*arrowSize],[y_tagged(i,f) y_tagged(i,f)+sin(t_tagged(i,f))*arrowSize]); 
%         end
        
        
        % Plot Sharks
        for f = 1 : N_fish
           plot(x(i,f),y(i,f),'o'); 
           plot([x(i,f) x(i,f)+cos(t(i,f))*arrowSize],[y(i,f) y(i,f)+sin(t(i,f))*arrowSize]); 
        end
        
        % Plot Robots
%         for r = 1 : N_robots
%             plot(robots(r,1),robots(r,2),'square',...
%                 'MarkerSize',20, 'MarkerFaceColor', [.49 1 .63]);
%             plot([robots(r,1) robots(r,1)+cos(robots(r,3))*arrowSize],[robots(r,2) robots(r,2)+sin(robots(r,3))*arrowSize]); 
%             circle(robots(r,1),robots(r,2), range);   
%         end

        % Plot Particles
        for h=1:N_part
            plot(p(h, 1), p(h,2), '.', 'MarkerSize', 10);
            plot(p(h, 3), p(h,4), '.', 'MarkerSize', 10);
        end

        % Plot Particle Mean Line
        plot([p_mean(1), p_mean(3)], [p_mean(2), p_mean(4)]);
 

        % Plot Attraction Line
        plot([LINE_START(1), LINE_END(1)],[LINE_START(2), LINE_END(2)], 'black');

        title(seg_len_dist_i)
        pause(0.0001); 
    end
end



% Performance Criteria for numshark estimation
within_ns_limit = size(find( numshark_est > N_fish - 5 & numshark_est < N_fish + 5),1);

end


function h = circle(x,y,r)
% Plot Circle given point and radius
    th = 0:pi/50:2*pi;
    xunit = r * cos(th) + x;
    yunit = r * sin(th) + y;
    h = plot(xunit, yunit);
end
