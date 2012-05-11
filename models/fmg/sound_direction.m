function sound_direction( )

    global samplerate;
    global fs;

    grid = generate_square_grid();
    
    %Частота дискретизации АЦП
    samplerate = 4.8e4;
    
    %% Настройки приемной системы
    %Параметры приемного луча
    receive_ray.phi = 0.0;
    receive_ray.theta = 0;
    receive_ray.L = 5000;

    
    %% Настройки источника звука
    %Параметры источника звука
    snd_ray.phi = -0.4;
    snd_ray.theta = 0;
    snd_ray.L = 10000;
    [src_sound fs] = wavread('hello.wav');
    src_sound = src_sound(:,1);
    
    [res_sound partial_sigs] = phased_receive_signal(src_sound,grid,receive_ray,snd_ray);
    
    %xx = 1:1:length(partial_sigs{1,1});
    %plot(xx,partial_sigs{4,3},xx,partial_sigs{4,4});
    
    time_delays{1} = estimate_delta_phase(partial_sigs{4,1},partial_sigs{4,2},40);
    time_delays{2} = estimate_delta_phase(partial_sigs{4,2},partial_sigs{4,3},40);
    time_delays{3} = estimate_delta_phase(partial_sigs{4,3},partial_sigs{4,4},40);
    time_delays{4} = estimate_delta_phase(partial_sigs{4,4},partial_sigs{4,5},40);
    time_delays{5} = estimate_delta_phase(partial_sigs{4,5},partial_sigs{4,6},40);
    time_delays{6} = estimate_delta_phase(partial_sigs{4,6},partial_sigs{4,7},40);
    time_delays{7} = estimate_delta_phase(partial_sigs{4,7},partial_sigs{4,8},40);
    
    delta_distance{1} = 300000 * time_delays{1};
    delta_distance{2} = 300000 * time_delays{2};
    delta_distance{3} = 300000 * time_delays{3};
    delta_distance{4} = 300000 * time_delays{4};
    delta_distance{5} = 300000 * time_delays{5};
    delta_distance{6} = 300000 * time_delays{6};
    delta_distance{7} = 300000 * time_delays{7};

    valid_count = 0;
    distance = zeros(size(time_delays{1}));
    for ii=1:1:6
        [d cosa v] = estimate_distance(delta_distance{ii},delta_distance{ii+1});
        if ~v
            continue;
        end
        distance = distance + d;
        valid_count = valid_count+1;
    end
    
    distance = distance / valid_count;
    
    a = 160;
    acoss1 = -(a*a-delta_distance{3}.*delta_distance{3}-2*distance.*delta_distance{3}) ./ (2*distance*a);
    acoss2 = -(a*a-delta_distance{4}.*delta_distance{4}-2*distance.*delta_distance{4}) ./ (2*distance*a);
    %plot(delta_distance{1});
    
    acoss = mean([acoss1';acoss2']',2);
    
    
    plot((acos(acoss)-acos(snd_ray.phi))*180/pi);
    
end

function [d cosa valid] = estimate_distance(d1,d2)
    a = 160;
    d = abs((2*a*a - d1.*d1 - d2.*d2) ./ ...
        2 ./ ( d1 - d2));
    
    cosa = 0;
    if max(d(5000:10000))<10000
        valid = 1;
    else
        valid = 0;
    end
end







