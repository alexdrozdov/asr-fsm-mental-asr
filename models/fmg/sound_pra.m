function sound_pra()

    grid = generate_progressive_grid();
    
    %Частота дискретизации АЦП
    samplerate = 1e6;
    
    %% Настройки приемной системы
    %Параметры приемного луча
    receive_ray.phi = 0;
    receive_ray.theta = 0;
    receive_ray.L = 5000;
    
    t_delays_receive = eval_delays(grid,receive_ray); %Задержка распространения сигналов в аналоговой форме
    d_delays_receive = ceil(t_delays_receive / (1/samplerate));
    d_max_delay_receive = max(max(d_delays_receive));
    
    %Задержка сигнала, необходимая, чтобы сформировать фазовый фронт с
    %выбранного направления
    d_correct_receive = d_max_delay_receive - d_delays_receive;
    
    
    %% Настройки источника звука
    %Параметры источника звука
    snd_ray.phi = 0.9;
    snd_ray.theta = 0;
    snd_ray.L = 5000;
    
    t_delays_snd = eval_delays(grid,snd_ray);
    d_delays_snd = ceil(t_delays_snd / (1/samplerate));
    
    common_delays = d_correct_receive+d_delays_snd;
    common_delays = reshape(common_delays,size(common_delays,1)*size(common_delays,2),1);
    
    [src_sound fs] = wavread('hello.wav');
    src_sound = src_sound(:,1);
    dig_sound = resample(src_sound,samplerate,fs); %Формируем из исходного сигнала "выход" АЦП
    
    max_common_delay = max(common_delays);
    rest_signal_length = length(dig_sound) - max_common_delay; %Длина сигнала, которая остается при 
    % "вычитании" максимальной задержки. Все сигналы будут иметь такую
    % длину. Только положение сигналов будет отличаться
    
    len = length(common_delays);
    dig_sound_sum = zeros(rest_signal_length,1);
    for ii=1:1:len
        sig_start = common_delays(ii);
        sig_end   = common_delays(ii)+rest_signal_length-1;
        dig_sound_sum = dig_sound_sum + dig_sound(sig_start:sig_end);
    end
    
    res_sound = resample(dig_sound_sum/len,fs,samplerate);
    
    plot(res_sound);
    %wavplay(res_sound,fs);
end

function delays = eval_delays(grid,ray)

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


function grid = generate_square_grid()
    delta_x = 20;
    delta_y = 20;
    
    microphone_count_x = 8;
    microphone_count_y = 8;
    
    half_x = delta_x * (microphone_count_x-1) / 2;
    half_y = delta_y * (microphone_count_y-1) / 2;
    
    grid = cell(microphone_count_y,microphone_count_x);
    for ii=1:1:microphone_count_x
        for jj=1:1:microphone_count_y
            microphone.x = (ii-1)*delta_x - half_x;
            microphone.y = (jj-1)*delta_y - half_y;
            grid{jj,ii} = microphone;
        end
    end
end

function grid = generate_progressive_grid()
    %Размеры решетки
    aperture_x = 1000;
    aperture_y = 1000;
    
    microphone_count_x = 8;
    microphone_count_y = 8;
    
    qx = microphone_count_x-1;
    mx = (microphone_count_x-1) / 2;
    px = aperture_x / 2;
    ax = px / (mx*qx-mx*mx);
    bx = -ax*qx; 
    mlt_coefs_x = ((1:1:microphone_count_x)>microphone_count_x/2)*2 - 1;
    
    qy = microphone_count_y-1;
    my = (microphone_count_y-1) / 2;
    py = aperture_y / 2;
    ay = py / (my*qy-my*my);
    by = -ay*qy;
    mlt_coefs_y = ((1:1:microphone_count_y)>microphone_count_y/2)*2 - 1;

    
    
    grid = cell(microphone_count_y,microphone_count_x);
    for ii=1:1:microphone_count_x
        for jj=1:1:microphone_count_y
            microphone.x = (ax*(ii-1)*(ii-1)+bx*(ii-1)+px) * mlt_coefs_x(ii);
            microphone.y = (ay*(jj-1)*(jj-1)+by*(jj-1)+py) * mlt_coefs_y(jj);
            grid{jj,ii} = microphone;
        end
    end
end

