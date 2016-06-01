load fishSimData.mat
% PF Constants
Height = 50;
Width = 50;
N_part = 50;
Sigma_mean = 0.1;
x_sharks = x(1000:end, :);
y_sharks = y(1000:end, :);
t_sharks = t(1000:end, :);
PF_sd = 1;

% Initialize States
p = initParticles(Height, Width, N_part);
estimated = mean(p);
for i = 1:3000
    disp(i)
    p = propagate(p, Sigma_mean);
    w = getParticleWeights(p, x_sharks(i,:), y_sharks(i,:), PF_sd);
    p = resample(p,w);
    p_mean = computeParticleMean(p,w);
    disp(p_mean)
    
    arrowSize = 1.5;
    fig = figure(1);
    clf;
    hold on;
    for f=1:N_fish
       plot(x_sharks(i,f),y_sharks(i,f),'o'); 
       plot([x_sharks(i,f) x_sharks(i,f)+cos(t_sharks(i,f))*arrowSize],[y_sharks(i,f) y_sharks(i,f)+sin(t_sharks(i,f))*arrowSize]); 
    end
    
    for g=1:N_part
        plot(p(g, 1), p(g,2), '.');
        plot(p(g, 3), p(g,4), '.');
    end
    
    plot([p_mean(1), p_mean(3)], [p_mean(2), p_mean(4)])
    
    plot([LINE_START(1), LINE_END(1)],[LINE_START(2), LINE_END(2)])
    scale = 0.5;
    axis(scale*[-width width -width width]);
 
    pause(0.0001); 
end