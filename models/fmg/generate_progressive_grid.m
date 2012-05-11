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