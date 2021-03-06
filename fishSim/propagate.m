function p = propagate(p, sigma_mean, ns_t2, LINE_START, LINE_END)
%% Propagates particles by one move
    sigma = 0;

    for indi_p = 1:size(p,1)
        x1 = p(indi_p, 1) + normrnd(0, sigma_mean);
        y1 = p(indi_p, 2) + normrnd(0, sigma_mean);
        x2 = p(indi_p, 3) + normrnd(0, sigma_mean);
        y2 = p(indi_p, 4) + normrnd(0, sigma_mean);  
%         x1 = LINE_START(1);
%         y1 = LINE_START(2);
%         x2 = LINE_END(1);
%         y2 = LINE_END(2);
        num_shark = p(indi_p, 5) + sigma*(p(indi_p,5) - ns_t2(indi_p))...
            + normrnd(0,1); % TODO: currently using uniform
        num_shark = 100;
        if num_shark < 0
            num_shark = randi([0, 100]);
        end
        
        p(indi_p, :) = [x1, y1, x2, y2, num_shark];
        
    end
end
