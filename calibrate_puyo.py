import json
import numpy as np
import os.path
import mss
from calibrate_scrn import cell_height, cell_width
from PIL import Image, ImageStat, ImageOps, ImageDraw

# Current directory
directory = os.path.dirname(os.path.abspath(__file__))

# Isolate a Puyo. field = field image, rowcol = (row, col)
# This function doesn't use zero indexed positions...
def isolatePuyo(field, row, col, show = False):
    left = cell_width * (col - 1)
    right = cell_width * col
    up = cell_height * (row - 1)
    down = cell_height * row
    box = (left, up, right, down)
    puyo = field.crop(box)
    
    if show is True:
        puyo.show()

    return(puyo)

# Get RGB of one cell
def getCellRGB(field, row, col):
    puyo = isolatePuyo(field, row, col)

    # Only calculate mean for an ellipse inside the cell, to avoid
    # the mean getting thrown off by character backgrounds.
    size = (cell_width, cell_height)
    puyo_ellipse = Image.new('L', size, 0)
    draw = ImageDraw.Draw(puyo_ellipse)
    draw.ellipse((0, cell_height * 0.1) + (cell_width, cell_height), fill = 255)
    color = ImageStat.Stat(puyo, mask=puyo_ellipse).mean
    return(color)


# Get RGB triplet for all cells
def getFieldRGB(field):
    rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    cols = [1, 2, 3, 4, 5, 6]

    # Isolate a Puyo
    colordata = []
    for row in rows:
        rowdata = []
        for col in cols:
            color = getCellRGB(field, row, col)
            rowdata.append(color)
        colordata.append(rowdata)
    return colordata

## Calibrate Puyo colors using a sample field with all 5 colors and ojama.
if __name__ == '__main__':
    test_field = Image.open(directory + '/img/calibration/test_field.png')
    color_data = getFieldRGB(test_field)
    # Manually identify the Puyo colors using zero-indexed matrix coord
    # Top row with the Red X = 0.
    # Left most column = 0.
    purple = np.array([color_data[0][5],
                    color_data[0][0],
                    color_data[1][3],
                    color_data[2][1],
                    color_data[2][3],
                    color_data[3][1],
                    color_data[3][4]])
    red = np.array([color_data[0][1],
                    color_data[0][3],
                    color_data[1][1],
                    color_data[1][4],
                    color_data[1][5],
                    color_data[3][0],
                    color_data[3][2]])
    green = np.array([color_data[2][4],
                    color_data[4][1],
                    color_data[6][3],
                    color_data[10][1],
                    color_data[10][2],
                    color_data[10][5]])
    blue = np.array([color_data[0][4],
                    color_data[2][0],
                    color_data[3][5],
                    color_data[4][0],
                    color_data[4][2],
                    color_data[5][1],
                    color_data[5][4]])
    yellow = np.array([color_data[1][0],
                    color_data[2][5],
                    color_data[3][3],
                    color_data[5][0],
                    color_data[5][3],
                    color_data[5][5]])
    ojama = np.array([color_data[4][3],
                    color_data[5][2],
                    color_data[11][5]])
    RGB_data = {'P': np.mean(purple, axis=0),
                'R': np.mean(red, axis=0),
                'G': np.mean(green, axis=0),
                'B': np.mean(blue, axis=0),
                'Y': np.mean(yellow, axis=0),
                'J': np.mean(ojama, axis=0)}
    # Write JSON file with settings
    for key, value in RGB_data.items():
        RGB_data[key] = RGB_data[key].tolist()
    settings = {"RGB_data": RGB_data}
    json.dump(settings, open("puyo_settings.json","w"))


## Load calibration from JSON file
RGB_data = json.load(open("puyo_settings.json"))['RGB_data']


# Guess a cell's color by referencing the above RGB triplets
def getPuyoColor(puyo, threshold=0.2):
    LL = 1 - threshold  # lower limit
    UL = 1 + threshold  # upper limit
    if (puyo[0] > RGB_data['R'][0] * LL and puyo[0] < RGB_data['R'][0] * UL and
        puyo[1] > RGB_data['R'][1] * LL and puyo[1] < RGB_data['R'][1] * UL and
            puyo[2] > RGB_data['R'][2] * LL and puyo[2] < RGB_data['R'][2] * UL):
        return str('R')
    elif (puyo[0] > RGB_data['G'][0] * LL and puyo[0] < RGB_data['G'][0] * UL and
          puyo[1] > RGB_data['G'][1] * LL and puyo[1] < RGB_data['G'][1] * UL and
            puyo[2] > RGB_data['G'][2] * LL and puyo[2] < RGB_data['G'][2] * UL):
        return str('G')
    elif (puyo[0] > RGB_data['B'][0] * LL and puyo[0] < RGB_data['B'][0] * UL and
          puyo[1] > RGB_data['B'][1] * LL and puyo[1] < RGB_data['B'][1] * UL and
            puyo[2] > RGB_data['B'][2] * LL and puyo[2] < RGB_data['B'][2] * UL):
        return str('B')
    elif (puyo[0] > RGB_data['Y'][0] * LL and puyo[0] < RGB_data['Y'][0] * UL and
          puyo[1] > RGB_data['Y'][1] * LL and puyo[1] < RGB_data['Y'][1] * UL and
            puyo[2] > RGB_data['Y'][2] * LL and puyo[2] < RGB_data['Y'][2] * UL):
        return str('Y')
    elif (puyo[0] > RGB_data['P'][0] * LL and puyo[0] < RGB_data['P'][0] * UL and
          puyo[1] > RGB_data['P'][1] * LL and puyo[1] < RGB_data['P'][1] * UL and
            puyo[2] > RGB_data['P'][2] * LL and puyo[2] < RGB_data['P'][2] * UL):
        return str('P')
    elif (puyo[0] > RGB_data['J'][0] * LL and puyo[0] < RGB_data['J'][0] * UL and
          puyo[1] > RGB_data['J'][1] * LL and puyo[1] < RGB_data['J'][1] * UL and
            puyo[2] > RGB_data['J'][2] * LL and puyo[2] < RGB_data['J'][2] * UL):
        return str('J')
    else:
        return str('0')


# Guess cell colors for a whole field
def getFieldPuyoColors(field):
    color_data = getFieldRGB(field)
    matrix = np.array([['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0'],
                       ['0', '0', '0', '0', '0', '0']])
    for index1, row in enumerate(color_data):
        for index2, col in enumerate(row):
            matrix[index1 + 1, index2] = getPuyoColor(
                color_data[index1][index2])
    return matrix
