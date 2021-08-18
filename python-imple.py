import numpy as np
from math import pi, cos, sin, sqrt

# define hyperparameters
canvas_height = 80
canvas_width = 300
R = 350
r = 50
h = 100
d = 1000
del_theta = 0.03
light_source = np.array([-0.8, 0, 0.6])
canvas_z = 300

file = open("output.log", 'w')

ILL_CHAR_MAP = ['.', ',', '-', ';', ':', ';', '=', '!', '*', '#', '$', '@']
ILL_INT_MAP = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

class Point():
  def __init__(self, p) -> None:
    self.x = p[0]
    self.y = p[1]
    self.z = p[2]
  
  # get norm of the point
  def norm(self):
    x, y, z = self.x, self.y - h, self.z - d
    ratio = R / sqrt(x**2 + z**2)
    result_v = np.array([x - x * ratio, 
                        y, 
                        z - z * ratio])
    return result_v / sum(result_v**2)**0.5
  
  def get_distance(self):
    return sqrt(self.x**2 + self.y**2 + self.z**2)
  
  # get illuminus of the point
  def get_illuminus(self):
    return max(-np.dot(self.norm(), light_source), 0)
  
  # get char representing illuminus 
  def get_illumi_char(self):
    illumi = self.get_illuminus() * len(ILL_CHAR_MAP)  # TODO: change back to char map
    # return str(int(illumi))
    return ILL_CHAR_MAP[int(illumi)]

# generate donout pixel set
pixels = []
y_rotate_M_ = np.array([[cos(del_theta), 0, -sin(del_theta), 0], 
                       [0, 1, 0, 0],
                       [sin(del_theta), 0, cos(del_theta), 0],
                       [0, 0, 0, 1]])
move_M = np.array([[1, 0, 0, 0],
                    [0, 1, 0, h], 
                    [0, 0, 1, d],
                    [0, 0, 0, 1]])
# y_rotate_M = y_rotate_M_ / sum(y_rotate_M_**2)
for alpha in np.arange(0, 2*pi, del_theta):
  c_p = np.array([R + r * cos(alpha), r * sin(alpha), 0, 1])# pixel on the circle
  for n in range(int(2*pi/del_theta)):
    c_p = np.dot(y_rotate_M_, c_p) # pixel on the donout
    d_p = np.dot(move_M, c_p)
    pixels.append(Point(d_p))

# function for mapping value to 2d
point_matrix_2d = np.array([None] * canvas_width * canvas_height).reshape((canvas_height, canvas_width))
for p in pixels:
  x, y, z = p.x, p.y, p.z
  ratio = canvas_z / z
  x_trans = x * ratio
  y_trans = y * ratio
  
  pre_point = point_matrix_2d[int(y_trans), int(x_trans)]
  file.write(str(x_trans) + ' ' + str(y_trans) + '\n')
  # file.write(str(int(x_trans)) + ' ' + str(int(y_trans)) + '\n')
  # take the point with shortest distance from origin, where the viewer lies
  if (not pre_point) or (pre_point and pre_point.get_distance() > p.get_distance()):
    point_matrix_2d[int(y_trans), int(x_trans) + canvas_width // 2] = p

# # get final ouput matrix by getting illuminus from each point
# illuminus_matrix_2d = np.array([" "] * canvas_width * canvas_height).reshape((canvas_height, canvas_width))
# for i in range(canvas_height):
#   for j in range(canvas_width):
#     if point_matrix_2d[i, j]:
#       illuminus_matrix_2d[canvas_height - i - 1, j] = point_matrix_2d[i, j].get_illumi_char()

# # generate function define reflection from light ray
# for list in illuminus_matrix_2d:
#   for i in list:
#     file.write(i)
#   file.write('\n')
# file.close()
