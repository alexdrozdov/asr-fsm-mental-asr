function [angles] = distance_angle(AB, dl, distance)
	angles = acos(sqrt((AB^2/4 + distance.^2).^2./(AB^2 .* distance.^2) - (AB^2/2+2*distance.^2-dl^2).^2 ./ (4*AB^2 .* distance.^2)));
end