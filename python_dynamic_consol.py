import curses
import math
from time import sleep
import numpy as np

matrix = np.array([['1','2','3'], ['2','3','4']])

def main(stdscr):
  curses.curs_set(0)
  for i in range(len(matrix)):
    stdscr.addstr(i, 0, ''.join(matrix[i]))
  stdscr.refresh()
  sleep(3)

curses.wrapper(main)