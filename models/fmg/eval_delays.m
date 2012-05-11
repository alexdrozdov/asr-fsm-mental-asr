function [delays] = eval_delays(grid,ray)
%Определяет задержку, с которой сигнал достигает каждого микрофона в решетке
%Источник сигнала задан параметром ray

    %Положение конца вектора относительно центра решетки
    x = cos(pi/2 - ray.phi) * ray.L;
    y = sin(pi/2 - ray.phi) * ray.L * sin(ray.theta);
    z = sin(pi/2 - ray.phi) * ray.L * cos(ray.theta);
    
    delays = zeros(size(grid));
    for ii=1:1:size(grid,2)
        for jj=1:1:size(grid,1)
            L = sqrt( ...
                (x-grid{jj,ii}.x)^2 + ...
                (y-grid{jj,ii}.y)^2 + ...
                z^2 );
            t = L / 300000;
            delays(jj,ii) = t;
        end
    end
end