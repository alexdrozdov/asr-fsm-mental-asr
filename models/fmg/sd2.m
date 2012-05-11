function sd2( )

    global samplerate;
    global fs;

    grid = generate_square_grid();
    
    %Частота дискретизации АЦП
    samplerate = 100e3;%4.8e4;

    
    %% Настройки источника звука
    %Параметры источника звука
    snd_ray.phi = cos(85 *pi/180);
    snd_ray.theta = 0;
    snd_ray.L = 10000;
    [src_sound fs] = wavread('hello.wav');
    src_sound = src_sound(:,1);
    
    [res_sound partial_sigs] = receive_signal(src_sound,grid,snd_ray);
    
    %xx = 1:1:length(partial_sigs{1,1});
    %plot(xx,partial_sigs{4,3},xx,partial_sigs{4,4});
    
    time_delays{1} = estimate_delta_phase(partial_sigs{4,4},partial_sigs{4,5},40);
    delta_distance = 300000 * time_delays{1};
    size(delta_distance)
    delta_distance(5000)
    %plot(distance, distance_angle(0.1, 0.09,distance)*180/pi)
    distance_angle(100, delta_distance(5000),3000)*180/pi
end





