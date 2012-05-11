function grid = generate_square_grid()
    delta_x = 100;
    delta_y = 100;
    
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