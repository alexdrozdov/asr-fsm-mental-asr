function [zone] = near_zone(task_struct)
% Расчет ближней зоны на основании заданных параметров.
% 
% task_struct - набор параметров для моделирования ближней зоны
% Обязательные поля структуры
%  max_angle_error - максимальная погрешность определения угла (в градусах)
%  grid_step       - расстояние между микрофонами в решетке (в метрах)
% Дополнительные поля структуры
%  def_near_zone   - размер ближней зоны по-умолчанию
%  def_angles      - набор углов, для которых необходимо определить ближнюю зону (в градусах)
%  def_distance    - расстояние, на котором будут проводиться дальнейшие определения углов (в метрах)
% Поля структуры, управляющие визуализацией
%  show_plot       - Показать график                  [=1]
%  create_file     - Экспортировать результаты в файл [=0]
%  create_tex      - Экспортировать результаты в tex  [=0]
%  data_file_name  - Имя файла для экспорта данных
%  tex_file_name   - Имя файл tex

	%Обработка основных параметров запуска функции
	S  = task_struct.grid_step;
	da = task_struct.max_angle_error * pi/180;
	
	%Обработка дополнительных параметров запуска, влияющих на расчет ближней зоны
	if isfield(task_struct, "def_near_zone")
		L_0 = task_struct.def_near_zone;
	else
		L_0 = task_struct.grid_step * 5;
	end
	
	if isfield(task_struct, "def_angles")
		angles = task_struct.def_angles;
	else
		angles = 5:1:175;
	end;
	
	if isfield(task_struct, "def_distance")
		L = task_struct.def_distance;
	else
		L = 10;
	end;
	
	%Обработка параметров запуска, влияющих на визуализацию и экспорт результатов
	if ~isfield(task_struct, "show_plot")
		task_struct.show_plot = 1;
	end
	if ~isfield(task_struct, "create_file")
		task_struct.create_file = 0;
	end
	if ~isfield(task_struct, "create_tex")
		task_struct.create_tex = 0;
	end

	alpha_0 = angles.*pi/180;
	
	% Разность хода волн от истоника до микрофонов при размещении источника на расстоянии L0 на направлениях angle
	delta_l0=sqrt(S^2/4+S*L_0.*cos(alpha_0)+L_0^2)-sqrt(S^2/4-S*L_0.*cos(alpha_0)+L_0^2);
	
	% Направление, которое будет рассчитано на основании разности хода волн, если предположить что источик находится на расстоянии L
	cos_alpha=sqrt((S^2/4+L^2)^2-(S^2/4+L^2-delta_l0.^2/2).^2)/(S*L); 
	alpha = acos(cos_alpha);
	
	%Уточненные размеры ближне зоны
	L_near = sqrt((delta_l0.^4-delta_l0.^2*S^2)./(4*(delta_l0.^2-S^2*(cos(alpha-da)).^2)));
	L_near_max = max(L_near);
	
	if task_struct.show_plot
		polar([alpha_0;alpha_0]', [L_near; ones(1,size(L_near,2))*L_near_max]');
	end
	
	if task_struct.create_file
		fd = fopen(task_struct.data_file_name, "wt");
	    fprintf(fd, "%14.6f %14.6f\n", [alpha_0; L_near]);
	    fclose(fd);
	end
	
	if task_struct.create_tex
		fd = fopen("nz_gnuplot_data.dat", "wt");
	    fprintf(fd, "%14.6f %14.6f\n", [alpha_0; L_near]);
	    fclose(fd);
	    
	    if system("gnuplot ./nz_gnuplot.plt","sync")
	    	disp "Произошла ошибка при вызове gnuplot для формирования tex файла"
	    else
	    	system(["mv ./nz_gnuplot.tex ", task_struct.tex_file_name], "sync");
	    end
	    
	    unlink("nz_gnuplot_data.dat");
	end
	
	if 1==nargout
		zone = L_near;
	end
end