# 3d-object-displaying

dynamically displaying a rotating 3d donut in console, using characters to distinguish brightness of different part of the donout. 

## install 
This project was created under Mac OS, requires Python numpy==1.19.4. Other imported packegs (curses, math, time) are installed by default. 

## usage
run `python3 donut-to-view-imple.py` in root directory of the project will display the donut rotating in the console. Note that this is in a infinit loop, to stop, press Ctrl-c. 

(Working In Progress)
run `python3 view-to-donut-imple.py` will execute the second program that do the same thing as the first one, but this use a different implementation. 
If you are interested in the detailed difference: The first program take samples from the donut and map to the canvas, while this program take sample from donut where lies in the 'sight' of the canvas. The second algorithm is expected to take less time and display more accurately. 

Report PDF in Chinese is available in 'report' folder, report is based on the first implementation.

## Contributing
idea originated from https://www.youtube.com/watch?v=sW9npZVpiMI&t=163s
referenced: Imperial College London 3rd year material https://materials.doc.ic.ac.uk/resources/2021/60021
all code originated from Shitong Xu