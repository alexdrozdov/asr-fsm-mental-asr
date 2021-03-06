function [time_delays] = estimate_delta_phase(sig_1,sig_2,max_delay)
%Определяет разность фаз между двумя сигналами
%
%[time_delays] = estimate_delta_phase(sig_1,sig_2,max_delay)
%sig_1, sig_2 - сигналы, для которых необходимо определить сдвиг
%max_delay    - максимальное значение сдвига, на которое необходимо проверить сигналы

    off_sig_1 = cell(max_delay+1,1);
    off_sig_2 = cell(max_delay+1,1);
    delta_pow_1 = cell(max_delay+1,1);
    delta_pow_2 = cell(max_delay+1,1);
    
    len = length(sig_1);
    off_sig_1{1} = sig_1;
    delta_pow_1{1} = (off_sig_1{1} - sig_2).^2;
    
    filt_coeffs = [0.126223447257957,0.00863682139528565,0.00891019314105622,0.00920089527517415,0.00947489054236816, ...
                   0.00975306210407773,0.0100188878081460,0.0102762231106737,0.0105167921035544,0.0107671985598613, ...
                   0.0109979484564506,0.0112419301405110,0.0114900249123558,0.0116900716118703,0.0118671719036502,0.0121025385377515, ...
                   0.0122912719432313,0.0124737452849032,0.0126544695578234,0.0128077344060621,0.0129658822566100,0.0131002038852402, ...
                   0.0132531922605969,0.0133392489102483,0.0135256065969685,0.0135641749547635,0.0135401883901736,0.0137338041897202, ...
                   0.0137722780263331,0.0138354604477097,0.0138178747842321,0.0138445936928442,0.0138122613043111,0.0138445936928442, ...
                   0.0138178747842321,0.0138354604477097,0.0137722780263331,0.0137338041897202,0.0135401883901736,0.0135641749547635, ...
                   0.0135256065969685,0.0133392489102483,0.0132531922605969,0.0131002038852402,0.0129658822566100,0.0128077344060621, ...
                   0.0126544695578234,0.0124737452849032,0.0122912719432313,0.0121025385377515,0.0118671719036502,0.0116900716118703, ...
                   0.0114900249123558,0.0112419301405110,0.0109979484564506,0.0107671985598613,0.0105167921035544,0.0102762231106737, ...
                   0.0100188878081460,0.00975306210407773,0.00947489054236816,0.00920089527517415,0.00891019314105622,0.00863682139528565,0.126223447257957];
    
    flt_1 = filter(filt_coeffs,1,delta_pow_1{1});

    filtered_matrix = zeros(len,max_delay*2+1);
    filtered_matrix(:,max_delay+1) = flt_1;
    
    for offs=1:1:max_delay
        off_sig_1{offs+1} = [zeros(offs,1); sig_1(1:(len-offs))];
        off_sig_2{offs+1} = [zeros(offs,1); sig_2(1:(len-offs))];
        
        delta_pow_1{offs+1} = (off_sig_1{offs+1} - sig_2).^2;
        delta_pow_2{offs+1} = (off_sig_2{offs+1} - sig_1).^2;
        
        %plot(delta_pow_2{offs+1});
        
        flt_1 = filter(filt_coeffs,1,delta_pow_1{offs+1});
        flt_2 = filter(filt_coeffs,1,delta_pow_2{offs+1});
        
        filtered_matrix(:,max_delay-offs+1) = flt_1;
        filtered_matrix(:,max_delay+offs+1) = flt_2;
    end
    
    [m i] = min(filtered_matrix,[],2);
    
    xx = 1:1:len;
    %plot(xx,filtered_matrix(:,4),xx,filtered_matrix(:,3));
    %plot(xx,sig_1,xx,off_sig_2{3});
    
    global samplerate;
    %plot(xx,m,xx,(i-max_delay-1)/samplerate);
    time_delays = (i-max_delay-1)/samplerate;
end

