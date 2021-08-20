import numpy as np
from math import pi, cos, sin, sqrt, acos
from time import sleep
import curses

DEBUG = False

def norm(v):
  return v / sum(v**2)**0.5

# define hyperparameters
canvas_height = 50
canvas_width = 170
R = 100
r = 40
h = 200
d = 1000
del_theta = 0.1
light_direction = np.array([1, -1, 1])
light_direction = norm(light_direction)
canvas_z = 100
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
ILL_INT_MAP = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*']

class Point():
  def __init__(self, p) -> None:
    self.x = x = p[0]
    self.y = y = p[1]
    self.z = z = p[2]

    z -= d
    y -= h
    ratio = R / sqrt(x**2 + z**2)
    self.norm = norm(np.array([x - x * ratio, 
                              y, 
                              z - z * ratio]))
    self.norm = np.append(self.norm, [1])
  
  # get norm of the point
  def get_norm(self):
    return self.norm[:3]
  
  def get_distance(self):
    return sqrt(self.x**2 + self.y**2 + self.z**2)
  
  # get illuminus of the point, in radius angular value
  def get_illuminus(self):
    # return abs(np.dot(self.get_norm(), light_direction))
    # if DEBUG:
    #   print(np.dot(self.get_norm(), light_direction))
    return acos(np.dot(self.get_norm(), light_direction)) / pi
  
  # get char representing illuminus 
  def get_illumi_char(self):
    # take min to ensure value in range of ILL_CHAR_MAP
    illumi = min(self.get_illuminus() * len(ILL_CHAR_MAP), len(ILL_CHAR_MAP)-1)
    if DEBUG:
      print(self.get_illuminus())
    # if int(illumi) == 0:
    #   print(f'{illumi}') 
    # return str(int(illumi))
    return ILL_CHAR_MAP[int(illumi)]

  # apply rotate transform to the point, including its norm
  def rotate(self, trans_M):
    x, y, z = self.x, self.y, self.z
    self.x, self.y, self.z, _ = np.dot(trans_M, [x, y, z, 1])
    self.norm = np.dot(trans_M, self.norm)

  # apply move transform to the point, not apply to the norm vector
  def move(self, trans_M):
    x, y, z = self.x, self.y, self.z
    self.x, self.y, self.z, _ = np.dot(trans_M, [x, y, z, 1])

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
    if x_index >= (canvas_width // 2) or y_index >= canvas_height \
       or x_index < (- canvas_width // 2) or y_index < 0:
      continue

    # showing pixel visible from viewer:
    # # method 1: take the point with shortest distance from origin, where the viewer lies
    # pre_point = point_matrix_2d[y_index, x_index + canvas_width // 2]

    # if (not pre_point) or (pre_point and pre_point.get_distance() > p.get_distance()):
    #   point_matrix_2d[y_index, x_index + canvas_width // 2] = p

    # # method 2: take the surface with norm of reverse direction of the view line
    # if np.dot(np.array([x, y, z]), p.norm()) <= 0:
    #   point_matrix_2d[y_index, x_index + canvas_width // 2] = p

    # method 3: combine two approaches
    pre_point = point_matrix_2d[y_index, x_index + canvas_width // 2]

    if np.dot(np.array([x, y, z]), p.get_norm()) <= 0:
      # new point face the view direction
      if (not pre_point) or (pre_point and pre_point.get_distance() > p.get_distance()):
        # new point is closer to the viewer
        point_matrix_2d[y_index, x_index + canvas_width // 2] = p


  # get final ouput matrix by getting illuminus from each point
  illuminus_matrix_2d = np.array([" "] * canvas_width * canvas_height).reshape((canvas_height, canvas_width))
  for i in range(canvas_height):
    for j in range(canvas_width):
      if point_matrix_2d[i, j]:
        illuminus_matrix_2d[canvas_height - i - 1, j] = point_matrix_2d[i, j].get_illumi_char()
  
  return illuminus_matrix_2d

# getting (n, 4) np matrix for n points' position, 
# return (n, 4) matrix of transformed position
def rotate_donout(pixels):
  for p in pixels:
    # move donout back to origin
    p.move(move_M_inverse)
    # rotate
    xy_rotate_M = np.dot(x_rotate_M, y_rotate_M)
    p.rotate(xy_rotate_M)

    # move to the view position
    p.move(move_M)
  return pixels
    
# getting (n, 4) matrix, return list of n Pixels 
def to_Pixels(pixels_M):
  pixels = []
  for v in pixels_M:
    pixels.append(Point(v))
  return pixels

def main(stdscr):
  # initialize donout pixel set
  pixels_M = []

  for alpha in np.arange(0, 2*pi, del_theta):
    c_p = np.array([R + r * cos(alpha), r * sin(alpha), 0, 1])# pixel on the circle
    for n in range(int(2*pi/del_theta)):
      c_p = np.dot(y_rotate_M, c_p) # pixel on the donout
      d_p = np.dot(move_M, c_p)
      pixels_M.append(d_p)

  pixels = to_Pixels(pixels_M)

  # printing the rotating donout till program killed
  if DEBUG:
    for i in range(1):
      illuminus_matrix_2d = get_image(pixels)
    
      for j in range(len(illuminus_matrix_2d)): 
        line = illuminus_matrix_2d[j]
      pixels = rotate_donout(pixels)
  else:
    while True:
      illuminus_matrix_2d = get_image(pixels)
      
      for j in range(len(illuminus_matrix_2d)): 
        line = illuminus_matrix_2d[j]
        stdscr.addstr(j, 0, ''.join(line))
      stdscr.refresh()
      pixels = rotate_donout(pixels)


if DEBUG:
  main(None)
else:
  curses.wrapper(main)

