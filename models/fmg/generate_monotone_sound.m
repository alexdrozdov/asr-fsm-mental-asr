function [signal] = generate_monotone_sound(samplerate, time, frequency, amplitude, phase, filename)
% generate_monotone_sound - Функция формирует стерео звук с различными параметрами левого и правого канала
%
% samplerate - частота дискретизации
% time       - длительность сигнала в секундах
% frequency  - частота сигнала
% amplitude  - [left right] амлитуда сигнала в правом и левом канале
% phase      - [left right] фаза сигнала в левом и правом канале (в градусах)
% filename   - имя файла, в который должен быть сохранен сигнал

	len = samplerate * time;
	sig = [amplitude(1)*sin(2*(1:1:len)*pi*frequency(1)/samplerate + phase(1)*pi/180) ; ...
	       amplitude(2)*sin(2*(1:1:len)*pi*frequency(2)/samplerate + phase(2)*pi/180)]';
	       
	if exist('filename')
		wavwrite(sig,samplerate,filename);
	end
	
	if 1==nargout
	signal = sig;
	end
end