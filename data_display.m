data = load('output.log');
subplot(221);
plot(data(:, 1), data(:, 2));
title('x-y graph');
subplot(222);
plot(data(:, 2), data(:, 3));
title('y-z graph');
subplot(223);
plot(data(:, 1), data(:, 3));
title('x-z graph')