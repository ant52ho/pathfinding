# This is my a* program. Each section will be separated with a new title
from PIL import Image, ImageChops
from matplotlib.image import imread
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys
import os
print('modules done installing')

'''Section 1: Rotating, checking for entrance, and finding the path width'''
# gets user to input file name. OSError applies when entering the wrong file type. FilenotFoundError occurs when an inexistant file is entered
# finding path width is crucial to the efficiency of this program as it determines if the program scans maze photo pixel by pixel or 8 pixels by 8 pixels

while True:
    try:
        user_file = str(input('Enter file name. \nNote: File names are sensative. You must include their file type and ensure files are image files eg. maze_name.jpg\n'))
        maze = Image.open(user_file)
        break
    except FileNotFoundError:
        print('try again\n')
        continue
    except OSError:
        print('try again\n')
# This function can do a horizontal search of an image and return where a pattern is, or in this case the size of blank space caused from a gap in the entrance of the maze
def horizontal_search(width, y_value, image_file):
    width, height = image_file.size
    dot = image_file.load()
    avg_colour = []
    for x_value in range(width):
        if x_value == width-1:
            return None
        if dot[x_value, y_value] != dot[0,0]:
            for opening in range(x_value, width):
                if dot[opening,y_value] == dot[0,0]:
                    break
            return int((x_value+opening)/2)
entries = []
# This assumes the maze is a 4 sided shape and scans all four sides for an opening
for count in range(4):
    maze_width, maze_height = maze.size
    entries.append(horizontal_search(maze_width, 0, maze))
    maze = maze.rotate(90, expand = 1)
    maze.show()
    
# the program exits early if theres less than two openings or more than 2 openings. An instance of None represents a side without an opening. 
if entries.count(None) <= 1:
    print('more than two openings detected. Please exit the program.')
    sys.exit()
if entries.count(None) >= 3:
    print('only one or less entry detected. Please exit the program.')
    sys.exit()

# the image is rotated until an opening is at the top of the image. the number of rotations is saved as rotation_count
for rotation_count, number in enumerate(entries):
    if number != None:
        start_pixel = number
        maze = maze.rotate(360 - rotation_count*90, expand = 1)
        maze.save(user_file)
        break

# entries is refreshed for the amount of times the photo rotates. This helps when finding the end coordinate of the maze
for count in range(rotation_count):
    entries.append(entries[0])
    del entries[0]

# maze.load allows me to see the colour values of individual pixels. This can help determine the border colour
pixel = maze.load()
border_colour = pixel[0,0]
# pixels are scanned in a diagonal line from the top left to bottom right until one of another colour is found
for border_location in range(maze_height):
    if pixel[border_location, border_location] != border_colour:
        path_colour = pixel[border_location, border_location]
        # the diagonal pixel scanning process is repeated to measure the width of any path
        for path_width in range(border_location, maze_height):
            if pixel[path_width, path_width] != path_colour:
                break
        break

# path width is a measure of border+white path
path_width = path_width+1 # for rounding
pixel_search = int(path_width/2) # for future grouped sorting
# pixel_search is for an important aspect coming up. it determines the intensity of the area that is searched

'''Section 2: Converting the maze'''
def find_traversable(image_file):
    image_array = imread(image_file)
    average = np.mean(image_array)
    if average > 0.99: #1 is white, 0 is black. 
        return 0 # traversable
    else:
        return 1 # not traversable

# preparing to make a list of lists which will look be structured like a coordinate grid. My a* program is able to read the grid created in this section.
grid = []
row = []
top = 0
bottom = pixel_search

# this loop sections off the maze into tiny cubes with lengths of pixel_search. The average light values of these cubes are taken and replaced with a 0, meaning traversable, or 1, meaning non traversable. These values are stored into lists a row at a time then appended into this large list named 'grid' 
print('maze scanning...')
def find_traversable(image_file):
    image_array = imread(image_file)
    average = np.mean(image_array)
    if average > 0.99: #0.99 is light value
        return 0 # traversable
    else:
        return 1 # not traversable

# this turns the maze into a greyscale image
maze = Image.open(user_file)
maze_width, maze_height = maze.size

# variables are set to determine search area, unconstructed grid
pixel_search = 8
grid = []
row = []
top = 0
bottom = pixel_search
# .crop() is organised in left, top, right bottom in PIL
# first crop should start at 0 and crop pixel_search amount of pixels to the right

for vertical in range(pixel_search, maze_height+pixel_search)[::pixel_search]:
    row = []
    # the edges of the maze MUST be constructed to avoid missing an exit. If the bottom variable used in cropping is larger than the maze height, it is lowered. 
    if bottom > maze_height:
        bottom = maze_height
    for horizontal in range(pixel_search, maze_width+pixel_search)[::pixel_search]:
        if horizontal > maze_width:
            horizontal = maze_width
        # This part is where pillow comes in and crops. 
        interested_area = maze.crop((horizontal - pixel_search, top, horizontal, bottom))
        interested_area.save('focus.png')
        # a function is used here to see if a 0 or a 1 is to be appended
        if find_traversable('focus.png') == 0:
            row.append(0)
        else:
            row.append(1)
    # an entire row is appended and top, bottom are increased by pixel search to crop out the next row. 
    grid.append(row)
    top = top + pixel_search
    bottom = bottom + pixel_search

print('maze done scanning')

# obtains start tile
for x_val, row_value in enumerate(grid[0]):
    if row_value == 0:
        start = (x_val, len(grid)-1)

# obtains end tile
if entries[1] != None: #right
    for y_val, column_value in enumerate(grid):
            if column_value[-1] == 0:
                end = (len(column_value)-1, -1*y_val+len(grid)-1)
if entries[2] != None: #bottom
    for x_val, row_value in enumerate(grid[-1]):
        if row_value == 0:
            end = (x_val, 0)
if entries[3] != None: #left
    for y_val, column_value in enumerate(grid):
            if column_value[0] == 0:
                end = (0, -1*y_val+len(grid)-1)

'''Section 3: A* algorithm'''
# this uses the a* method to find a path from one point to another. My program uses lists to store info of the current square it is on. It is stored as followed:
# [coordinate, fvalue, gvalue, h_valueue, where it's from]
# for simplicity, their locations in the list have been turned into variables
print('pathfinding...')
Fval = 1
Gval = 2
h_value = 3
parent = 4

# this function finds the distance between any two points using the pythagorean theorem
def find_h(x1, y1, x2, y2):
    return int(round((((x1-x2)**2 + (y1-y2)**2))**(1/2), 0))

# this function checks if an inputted value is inside a specifically formatted . It will help during the A* algorithm
def in_list(value, the_list):
    for index, items in enumerate(the_list):
        if value == items[0]:
            return [True, index]
    return [False]

xlim = len(grid[0])-1
ylim = len(grid)-1
h_value = find_h(start[0], start[1], end[0], end[1])
current = [start, h_value, 0, h_value, None]
open_list = [current]
closed_list = []

# this program possibly goes on until all available points are searched
while open_list != []:
    # sorts the list by f value
    open_list.sort(key = lambda x:x[Fval])  
    # current becomes the lowest f value
    current = open_list[0]

    # if the current square is the final square
    if current[0] == end:
        total_path = [current[0]]
        # this part backtracks. The parent square of the end square is found, the parent square of that square is found, and so on. This goes on until the program reaches the first square 
        while current[0] != start:
            for lists in closed_list:
                if lists[0] == current[parent]:
                    current = lists
                    total_path.append(lists[0])
        break
    # the ideal next step is moved to the closed list
    del open_list[0]
    closed_list.append(current)

    # obtaining new position from current square
    for new_space in [(0,1), (1,0), (-1,0), (0,-1)]:
        child = (current[0][0] + new_space[0], current[0][1] + new_space[1])
        # if any coordinates are negative
        if child[0] < 0 or child[1] < 0:
            continue
        # if any coordinate is outside the boundary
        if child[0] > xlim or child[1] > ylim:
            continue
        # if the terrain is not traversable
        try:
            if grid[-1*child[1] + len(grid) -1][child[0]] != 0:
                continue
        except IndexError:
            continue
        gscore = current[Gval]+1
        # if child is in closed list
        if in_list(child, closed_list)[0] is True:
            continue
        # child data is calculated
        gscore = current[Gval]+1
        hscore = find_h(child[0], child[1], end[0], end[1])+1
        child_info = [child, gscore+hscore, gscore, hscore, current[0]]
        # if the child is not in the open lsit
        if in_list(child, open_list)[0] is False:
            open_list.append(child_info)
        # if the fvalue of the child is less than the current fvalue of the same tile
        else:
            # if child is already in the open list it checks if this new child is the best route
            falseindex = in_list(child, open_list)
            if child_info[Fval] < open_list[falseindex[1]][Fval]:
                open_list[falseindex[1]] = child_info

# if all options are scanned and there's nothing
if len(open_list) == 0:
    print('no exit ;/')
    sys.exit()

# the path that is found is put into a list called 'total_path'
print('path found')
total_path = total_path[::-1]

# this function turns values inside total_path into coordinates that matplotlib can read. 
def convertxy(alist):
    xval = []
    yval = []
    for instances in alist:
        xval.append(instances[0])
        yval.append(instances[1])
    return xval, yval

# coordinates are put into matplotlib and plotted
xy = convertxy(total_path)
plt.plot(xy[0],xy[1])
# the plotted image will have no axis and spacing will be scaled
plt.axis('off')
plt.axis('scaled')
plt.axis([-1, xlim, -1, ylim])
plt.savefig('path.png', transparent = True)
print('path photo created!')

'''Section 4: Cropping and resizing the path to fit maze'''
# this function trims the border off an image
def trim(image_file):
    background = Image.new(image_file.mode, image_file.size, image_file.getpixel((0,0)))
    diff = ImageChops.difference(image_file, background)
    bbox = diff.getbbox()
    if bbox:
        return image_file.crop(bbox)

# the ratio between image height to path height is important
path = Image.open('path.png')
path = trim(path)
path_width, path_height = (path.size)
width_ratio = maze_width/path_width
height_ratio = maze_height/path_height

# the maze is resized based on if any of its lengths are larger than the maze itself or if both of its lengths are smaller than the maze
if width_ratio < 1 or height_ratio < 1:
    # a smaller ratio means more to be resized
    # path is resized by height ratio
    if height_ratio < width_ratio:
        path_height = maze_height
        path_width = int(path_width*height_ratio)
        path = path.resize((path_width,path_height), Image.ANTIALIAS)
        path.save('path.png')
    else:
        # path is resized by width ratio
        path_width = maze_width
        path_height = int(path_height*width_ratio)
        path = path.resize((path_width,path_height), Image.ANTIALIAS)
        path.save('path.png')

# if path fits inside maze        
if width_ratio > 1 and height_ratio > 1:
    # smaller means that its closer to being regular size
    # path is resized by width ratio
    if width_ratio < height_ratio:
        path_width = maze_width
        path_height = int(path_height*width_ratio)
        path = path.resize((path_width,path_height), Image.ANTIALIAS)
        path.save('path.png')
    else:
        #path is resized by height ratio
        path_height = maze_height
        path_width = int(path_width*height_ratio)
        path = path.resize((path_width,path_height), Image.ANTIALIAS)
        path.save('path.png')
print('path photo cropped and resized')

'''Section 5: The resized path is correctly laid overtop the maze'''
# in this section, we scan each top pixel of the path photo and the pixel with the highest contrast compared to blank space is deemed as the start. This is done because although theres a nib of the path photo, sometimes the path is so compressed that the top pixel includes snippets of the path below. By looking for the pixel with the highest concentration of not-corner, we can guess the start of the path. 
pixel = path.load()
avg_colour = []
# for all top pixels in path
for x_val in range(path_width):
    # if a cropped area is unlike the corner pixel, then it is saved into a list
    if pixel[x_val, 0] != pixel[0,0]:
            small_space = path.crop((x_val-1, 0, x_val,1))
            small_space.save('focus.png')
            image_array = imread('focus.png')
            average = np.mean(image_array)
            avg_colour.append((average, x_val))
# the list is compared and the most defining pixel, or max, is chosen to represent the start of the path. 
nib = max(avg_colour)[1]
image_start = start_pixel - nib
# image is pasted onto the maze
maze.paste(path, (image_start, 2), path)
# maze, with the path printed onto it, is rotated accordingly to how many times it was rotated to become upright.
maze = maze.rotate(rotation_count*270, expand = 1)
maze.save('final.png')
# removes documents created during the program
os.remove('focus.png')
os.remove('path.png')
print('done')
