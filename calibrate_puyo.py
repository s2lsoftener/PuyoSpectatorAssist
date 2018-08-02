import numpy as np
import os.path
import mss
from PIL import Image
from PIL import ImageStat

# Current directory
directory = os.path.dirname(os.path.abspath(__file__))

# Function that crops a field down to each cell
def getCellColors(field):
    rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    cols = [1, 2, 3, 4, 5, 6]
    cellwidth = field.width / 6
    cellheight = field.height / 12

    # Isolate a Puyo
    colordata = []
    for row in rows:
        rowdata = []
        for col in cols:
            left = cellwidth * (col - 1)
            right = cellwidth * col
            up = cellheight * (row - 1)
            down = cellheight * row
            box = (left, up, right, down)
            region = field.crop(box)
            color = ImageStat.Stat(region).mean
            rowdata.append(color)
        colordata.append(rowdata)
    return colordata


# Calibrate Puyo colors using test_field.png
test_field = Image.open(directory + '/img/calibration/test_field.png')
color_data = getCellColors(test_field)
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
    color_data = getCellColors(field)
    print('got color data')
    # matrix = np.array([['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0'],
    #                    ['0', '0', '0', '0', '0', '0']])
    # print('made the matrix')
    # for index1, row in enumerate(color_data):
    #     for index2, col in enumerate(row):
    #         matrix[index1 + 1, index2] = str(getPuyoColor(
    #             color_data[index1][index2]))
    return matrix


