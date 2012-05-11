function [delta_l] = delta_path(task_struct)
% Расчет разности хода сигнала на основании заданных параметров.
% 
% task_struct - набор параметров для моделирования ближней зоны
% Обязательные поля структуры
%  grid_step       - расстояние между микрофонами в решетке (в метрах)
% Дополнительные поля структуры
%  def_angles      - набор углов, для которых необходимо определить разность хода (в градусах)
%  def_distance    - расстояние, на котором будут проводиться дальнейшие определения углов (в метрах)
% Поля структуры, управляющие визуализацией
%  show_plot       - Показать график                  [=0]

	%Обработка основных параметров запуска функции
	S  = task_struct.grid_step;
	
	%Обработка дополнительных параметров запуска, влияющих на расчет
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
		task_struct.show_plot = 0;
	end

	alpha_0 = (90-angles).*pi/180;
	
	% Разность хода волн от истоника до микрофонов при размещении источника на расстоянии L0 на направлениях angle
	delta_l0=sqrt(S^2/4+S*L.*cos(alpha_0)+L^2)-sqrt(S^2/4-S*L.*cos(alpha_0)+L^2);
	
	if nargout==1
		delta_l = delta_l0;
	end
	
	if task_struct.show_plot
		plot(angles, delta_l0);
	end
end