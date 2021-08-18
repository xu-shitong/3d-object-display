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

ILL_CHAR_MAP = ['.', ',', '-', ';', ':', ';', '=', '!', '*', '#', '$', '@']

class Point():
  def __init__(self, p) -> None:
    self.x = p[0]
    self.y = p[1]
    self.z = p[2]
  
  # get norm of the point
  def norm(self):
    x, y, z = self.x, self.y - h, self.z - d
    ratio = R / sqrt(x**2 + z**2)
    return norm(np.array([x - x * ratio, 
                        y, 
                        z - z * ratio]))
  
  def get_distance(self):
    return sqrt(self.x**2 + self.y**2 + self.z**2)
  
  # get illuminus of the point
  def get_illuminus(self):
    return max(-np.dot(self.norm(), light_direction), 0)
  
  # get char representing illuminus 
  def get_illumi_char(self):
    illumi = self.get_illuminus() * len(ILL_CHAR_MAP)
    # return str(int(illumi))
    return ILL_CHAR_MAP[int(illumi)]

# file is used for debug propose, display donout to console instead
# file = open("output.log", 'w')

def get_image(pixels):
  # mapping value to 2d
  point_matrix_2d = np.array([None] * canvas_width * canvas_height).reshape((canvas_height, canvas_width))
  for p in pixels:
    x, y, z = p.x, p.y, p.z
    ratio = canvas_z / z
    x_trans = x * ratio
    y_trans = y * ratio
    
    x_index, y_index = int(x_trans), int(y_trans)
    # ignore pixel out off canvas
    if (x_index + canvas_width // 2) >= canvas_width or y_index >= canvas_height \
       or x_index < (- canvas_width // 2) or y_index < 0:
      continue

    # file.write(str(x_trans) + ' ' + str(y_trans) + '\n')
    # file.write(str(int(x_trans)) + ' ' + str(int(y_trans)) + '\n')

    # showing pixel visible from viewer:
    # method 1: take the point with shortest distance from origin, where the viewer lies
    pre_point = point_matrix_2d[y_index, x_index]

    if (not pre_point) or (pre_point and pre_point.get_distance() > p.get_distance()):
      point_matrix_2d[y_index, x_index + canvas_width // 2] = p

    # # method 2: take the surface with norm of reverse direction of the view line
    # if np.dot(np.array([x, y, z]), p.norm()) <= 0:
    #   point_matrix_2d[y_index, x_index + canvas_width // 2] = p

    # method 3: combine two approaches
    # pre_point = point_matrix_2d[y_index, x_index]

    # if np.dot(np.array([x, y, z]), p.norm()) <= 0:
    #   # new point face the view direction
    #   if (not pre_point) or (pre_point and pre_point.get_distance() > p.get_distance()):
    #     # new point is closer to the viewer
    #     point_matrix_2d[y_index, x_index + canvas_width // 2] = p


  # get final ouput matrix by getting illuminus from each point
  illuminus_matrix_2d = np.array([" "] * canvas_width * canvas_height).reshape((canvas_height, canvas_width))
  for i in range(canvas_height):
    for j in range(canvas_width):
      if point_matrix_2d[i, j]:
        illuminus_matrix_2d[canvas_height - i - 1, j] = point_matrix_2d[i, j].get_illumi_char()
  
  return illuminus_matrix_2d

# getting (n, 4) np matrix for n points' position, 
# return (n, 4) matrix of transformed position
def rotate_donout(pixels_M):
  # move donout back to origin
  pixels_M = np.dot(pixels_M, move_M_inverse.T)
  # rotate
  xy_rotate_M = np.dot(x_rotate_M, y_rotate_M)
  pixels_M = np.dot(pixels_M, xy_rotate_M.T)

  # move to the view position
  return np.dot(pixels_M, move_M.T)

    
# getting (n, 4) matrix, return list of n Pixels 
def to_Pixels(pixels_M):
  pixels = []
  for v in pixels_M:
    pixels.append(Point(v))
  return pixels

def main(stdscr):
  # initialize donout pixel set
  pixels_M = []

  # y_rotate_M = y_rotate_M_ / sum(y_rotate_M_**2)
  for alpha in np.arange(0, 2*pi, del_theta):
    c_p = np.array([R + r * cos(alpha), r * sin(alpha), 0, 1])# pixel on the circle
    for n in range(int(2*pi/del_theta)):
      c_p = np.dot(y_rotate_M, c_p) # pixel on the donout
      d_p = np.dot(move_M, c_p)
      pixels_M.append(d_p)


  # for i in range(5):
  #   pixels_M = rotate_donout(pixels_M)

  # pixels = to_Pixels(pixels_M)
  # illuminus_matrix_2d = get_image(pixels)
  # # output to file
  # for j in range(len(illuminus_matrix_2d)): 
  #   list = illuminus_matrix_2d[j]
  #   for i in list:
  #     file.write(i)
  #   file.write('\n')
  # file.close()

  # printing the rotating donout till program killed
  while True:

    pixels = to_Pixels(pixels_M)
    illuminus_matrix_2d = get_image(pixels)
    
    for j in range(len(illuminus_matrix_2d)): 
      line = illuminus_matrix_2d[j]
      # print(''.join(line))
      stdscr.addstr(j, 0, ''.join(line))
    stdscr.refresh()
    sleep(0.05)
    pixels_M = rotate_donout(pixels_M)
curses.wrapper(main)

# main(None)