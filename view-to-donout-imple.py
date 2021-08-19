import numpy as np
from math import pi, cos, sin, sqrt
from time import sleep
import curses

def norm(v):
  return v / sum(v**2)**0.5

# define hyperparameters
canvas_height = 50
canvas_width = 170
R = 100
r = 40
h = 100
d = 1000
del_theta = 0.05
light_direction = np.array([0, 1, -1])
light_direction = norm(light_direction)
canvas_z = 300
y_rotate_M = np.array([[cos(del_theta), 0, -sin(del_theta), 0], 
                       [0,              1,               0, 0],
                       [sin(del_theta), 0,  cos(del_theta), 0],
                       [0,              0,               0, 1]])
x_rotate_M = np.array([[1,              0,               0, 0], 
                       [0, cos(del_theta), -sin(del_theta), 0],
                       [0, sin(del_theta),  cos(del_theta), 0],
                       [0,              0,               0, 1]])
move_M = np.array([[1, 0, 0, 0],
                   [0, 1, 0, h], 
                   [0, 0, 1, d],
                   [0, 0, 0, 1]])
move_M_inverse = np.array([[1, 0, 0, 0],
                           [0, 1, 0, -h], 
                           [0, 0, 1, -d],
                           [0, 0, 0, 1]])

ILL_CHAR_MAP = ['.', ',', '-', ':', ';', '=', '!', '*', '#', '$', '@']


file = open('output.log', 'w')
pixels_M = np.array([None] * canvas_height * canvas_width).reshape((canvas_height, canvas_width))
# get list of pixels visible to the viewer
for i in range(canvas_height):
  for j in range(canvas_width):
    # get view direction
    view_v = np.array([])