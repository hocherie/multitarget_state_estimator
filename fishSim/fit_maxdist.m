function max_dist = fit_maxdist(seg_length, density)

max_dist = 0.2612+ 0.01742*seg_length + 3.305*density + ...
     -5.202e-05*seg_length^2 + 0.000135*seg_length*density + ...
     -0.6829*density^2;
end