function [res_sound partial_sigs] = receive_signal(src_sound,grid,snd_ray)
%Обеспечивает прием сигнала с заданного направления без фазирования решетки
%
%[res_sound partial_sigs] = receive_signal(src_sound,grid,snd_ray)
%src_sound - исходный сигнал в источнике взука
%grid      - массив, описывающий строение микрофонной решетки. Для построения
%            массива могут использоваться функции generate_square_grid или generate_progressive_grid
%snd_ray   - направление, на котором находится источник звука

    global samplerate;
    global fs;
    
    original_fmg_size = size(grid);   
    
    t_delays_snd = eval_delays(grid,snd_ray);
    d_delays_snd = ceil(t_delays_snd / (1/samplerate));
    
    common_delays = d_delays_snd;
    common_delays
    common_delays = reshape(common_delays,size(common_delays,1)*size(common_delays,2),1);
    
    dig_sound = resample(src_sound,samplerate,fs); %Формируем из исходного сигнала "выход" АЦП
    full_sig_length = length(dig_sound);
    
    len = length(common_delays);
    dig_sound_sum = zeros(full_sig_length,1);
    partial_sigs_tmp = cell(len,1);
    for ii=1:1:len
        sig_start = common_delays(ii);
        sig_end   = full_sig_length-sig_start;
        offs_sig = [zeros(sig_start,1);dig_sound(1:sig_end)];
        partial_sigs_tmp{ii} = offs_sig;
        dig_sound_sum = dig_sound_sum + offs_sig;
    end
    
    partial_sigs = reshape(partial_sigs_tmp,original_fmg_size);
    res_sound = resample(dig_sound_sum/len,fs,samplerate);
end