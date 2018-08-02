import copy
import math
import webbrowser
import numpy as np

# test_matrix = np.array([['Y', 'Y', '0', '0', '0', '0'],
#                         ['Y', 'G', '0', '0', '0', '0'],
#                         ['P', 'G', '0', '0', '0', '0'],
#                         ['P', 'B', '0', '0', '0', '0'],
#                         ['G', 'B', '0', '0', '0', '0'],
#                         ['G', 'B', '0', '0', '0', '0'],
#                         ['R', 'R', '0', '0', '0', '0'],
#                         ['R', 'R', '0', '0', 'R', '0'],
#                         ['R', 'B', '0', '0', 'R', '0'],
#                         ['G', 'G', '0', '0', 'R', '0'],
#                         ['P', 'B', 'R', '0', 'R', '0'],
#                         ['P', 'J', 'Y', 'G', 'G', 'G'],
#                         ['R', 'B', 'G', 'G', 'G', 'G']])
# empty_matrix = np.array([['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0'],
#                          ['0', '0', '0', '0', '0', '0']])

# Constants
field_width = 6
field_height = 13
target_point = 70
puyo_to_clear = 4  # Number of Puyos required to make a group pop
color_bonus = [0, 3, 6, 12, 24]
group_bonus = [0, 2, 3, 4, 5, 6, 7, 10, 10, 10, 10, 10, 10, 10, 10,
               10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
               10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
               10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
               10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
               10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
chain_power = [0, 8, 16, 32, 64, 96, 128, 160, 192, 224,
               256, 288, 320, 352, 384, 416, 448, 480,
               512, 544, 576, 608, 640, 672]
game_colors = ['R', 'G', 'B', 'Y', 'P']  # Red, Green, Blue, Yellow, Purple
clear_hidden_ojama = True   # SEGA Puyo games allow clearing of 13th row ojama


# Cell-checking functions
def isPuyo(cell):
    return cell in game_colors


def isOjama(cell):
    return cell == 'J'


def checkAdjCells(matrix, rowcol):
    # Get row & col positions of cell from rowcol tuple
    row = rowcol[0]
    col = rowcol[1]

    adjacentPuyos = {}
    # Check Left. If it's in the leftmost col (0), nothing can be there.
    if(col > 0):
        if matrix[row, col - 1] != '0':
            adjacentPuyos['left'] = {
                'value': matrix[row, col - 1],
                'row': row,
                'col': col - 1,
                'colored': isPuyo(matrix[row, col - 1]),
                'ojama': isOjama(matrix[row, col - 1]),
                'same': matrix[row, col] == matrix[row, col - 1],
                'hidden': row == 0}
    # Check Up
    if(row > 0):
        if matrix[row - 1, col] != '0':
            adjacentPuyos['up'] = {
                'value': matrix[row - 1, col],
                'row': row - 1,
                'col': col,
                'colored': isPuyo(matrix[row - 1, col]),
                'ojama': isOjama(matrix[row - 1, col]),
                'same': matrix[row, col] == matrix[row - 1, col],
                'hidden': row == 0}
    # Check Right
    if(col < field_width - 1):
        if matrix[row, col + 1] != '0':
            adjacentPuyos['right'] = {
                'value': matrix[row, col + 1],
                'row': row,
                'col': col + 1,
                'colored': isPuyo(matrix[row, col + 1]),
                'ojama': isOjama(matrix[row, col + 1]),
                'same': matrix[row, col] == matrix[row, col + 1],
                'hidden': row == 0}
    # Check Down
    if(row < field_height - 1):
        if matrix[row + 1, col] != '0':
            adjacentPuyos['down'] = {
                'value': matrix[row + 1, col],
                'row': row + 1,
                'col': col,
                'colored': isPuyo(matrix[row + 1, col]),
                'ojama': isOjama(matrix[row + 1, col]),
                'same': matrix[row, col] == matrix[row + 1, col],
                'hidden': row == 0}
    return adjacentPuyos


# Check for pops
def checkPops(matrix):
    # Create a matrix that tracks which cells have already been tested
    checkMatrix = np.zeros((field_height, field_width))

    # Initialize other variables
    listGroups = []
    listColors = []
    listGroupSize = []
    anypops = False  # Any groups of four at all?

    # Loop through the matrix
    for index, cell in enumerate(np.nditer(matrix)):
        # Get current row and col
        row = math.floor(index / field_width)
        col = index % field_width

        # Check Puyos below 13th row that haven't been checked yet
        if (row != 0 and checkMatrix[row, col] == 0 and
                isPuyo(matrix[row, col])):
            current_group = [{'color': str(cell), 'row': row, 'col': col}]

            # Check adjacent Puyos and add them to current_group.
            # Iterate over current_group until it runs out of Puyos
            # to check
            for puyo in current_group:
                # Mark the cell as checked.
                checkMatrix[puyo['row'], puyo['col']] = 1

                # Check Adjacent Puyos
                adjPuyos = checkAdjCells(matrix, (puyo['row'], puyo['col']))
                for side, adjpuyo in adjPuyos.items():
                    if(adjpuyo['same'] and adjpuyo['hidden'] is False and
                            checkMatrix[adjpuyo['row'], adjpuyo['col']] == 0):
                        checkMatrix[adjpuyo['row'], adjpuyo['col']] = 1
                        current_group.append({
                            'color': adjpuyo['value'],
                            'row': adjpuyo['row'],
                            'col': adjpuyo['col']
                        })
            if len(current_group) >= puyo_to_clear:
                listGroups.append(current_group)
                listGroupSize.append(len(current_group))
                listColors.append(str(cell))
                anypops = True
    return {'groups': listGroups,
            'colors': listColors,
            'sizes': listGroupSize,
            'numcolors': len(set(listColors)),
            'popping': anypops}


def clearAdjOjama(matrix, row, col):
    matrix = copy.copy(matrix)
    if clear_hidden_ojama is True:
        row_height_limit = 0
    else:
        row_height_limit = 1

    if row > row_height_limit:
        if isOjama(matrix[row - 1, col]):
            matrix[row - 1, col] = "0"
    if row < 12:
        if isOjama(matrix[row + 1, col]):
            matrix[row + 1, col] = "0"
    if col > 0:
        if isOjama(matrix[row, col - 1]):
            matrix[row, col - 1] = "0"
    if col < 5:
        if isOjama(matrix[row, col + 1]):
            matrix[row, col + 1] = "0"
    return matrix


def popPuyos(matrix):
    matrix = copy.copy(matrix)
    for groups in checkPops(matrix)['groups']:
        for puyo in groups:
            matrix[puyo['row'], puyo['col']] = 0
            matrix = clearAdjOjama(matrix, puyo['row'], puyo['col'])
    return matrix


def applyGravity(matrix):
    matrix = copy.copy(matrix)
    matrix = np.transpose(matrix)
    for col in matrix:
        filter_empty = col[col != '0']
        if len(filter_empty) > 0:
            col[:] = '0'
            col[-len(filter_empty):] = filter_empty
    return np.transpose(matrix)


def simulateChain(matrix):
    matrix = copy.copy(matrix)
    # Initialize variables
    total_score = 0
    total_garbage = 0
    chain_length = 0
    NL = 0.0  # Initialize Leftover Nuisance Points
    matrix = applyGravity(matrix)

    if checkPops(matrix)['popping'] is False:
        return {'field': matrix,
                'chain': chain_length,
                'score': total_score,
                'ojama': total_garbage}
    else:
        while checkPops(matrix)['popping'] is True:
            pop_info = checkPops(matrix)
            chain_length += 1
            num_colors = pop_info['numcolors']
            group_sizes = pop_info['sizes']

            PC = sum(group_sizes)  # Total Puyos cleared in the chain
            CB = color_bonus[num_colors - 1]  # Color bonus

            GBs = []  # Get corresponding group bonuses for each group
            for group in group_sizes:
                GBs.append(group_bonus[group - puyo_to_clear])
            GB = sum(GBs)  # Sum group bonuses for each group

            CP = chain_power[chain_length - 1]  # Get chain power

            # (CB + GB + CP) has min/max values of 1 and 999
            if (CB + GB + CP) == 0:
                total_bonuses = 1
            elif (CB + GB + CP) > 999:
                total_bonuses = 999
            else:
                total_bonuses = (CB + GB + CP)

            # Calculate running score
            step_score = 10 * PC * total_bonuses

            # Calculate "Nuisance Points" NP
            NP = step_score / target_point + NL  # NP for this step
            NC = math.floor(NP)  # Nuisance to send
            NL = NP - NC

            total_score += step_score
            total_garbage += NC

            # Run chain to its next step
            matrix = applyGravity(popPuyos(matrix))
    return {'field': matrix,
            'chain': chain_length,
            'score': total_score,
            'ojama': total_garbage}


# Convenience function to export chains to Puyo Nexus simulator
def exportToPN(matrix):
    convert = {'R': 4,
               'G': 7,
               'B': 5,
               'Y': 6,
               'P': 8,
               'J': 1,
               '0': 0}

    PN_matrix = copy.copy(matrix)
    for index, cell in enumerate(np.nditer(PN_matrix)):
        row = math.floor(index / field_width)
        col = index % field_width
        PN_matrix[row, col] = convert[str(cell)]

    chaincode = str()
    for r in range(len(PN_matrix)):
        chaincode += np.array2string(PN_matrix[r]).replace(
            '[', '').replace("\'", "").replace(']', '').replace(' ', '')

    url = ('https://puyonexus.com/chainsim/?w=' + str(PN_matrix.shape[1]) +
           '&h=' + str(PN_matrix.shape[0] - 1) + '&chain=' + str(chaincode))
    webbrowser.open(url)
