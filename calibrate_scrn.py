import os.path
import mss
from PIL import Image


# Set monitor and screen regions
directory = os.path.dirname(os.path.abspath(__file__))
with mss.mss() as sct:
    monitor_info = sct.monitors[1]  # Set your monitor number

    # Full screenshot
    sct_img = sct.grab(monitor_info)
    monitor = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')

    # Set screen regions (Puyo Puyo Chronicle)
    Player1 = {
        'board': {'top': 115, 'left': 294, 'width': 432, 'height': 805},
        'next': {'top': 115, 'left': 726, 'width': 100, 'height': 200},
        'score': {'top': 930, 'left': 294, 'width': 432, 'height': 100}
    }
    Player1['next_bit'] = {
        'top': int(round(Player1['next']['top'] + Player1['next']['height'] * 0.1, 0)),
        'left': int(round(Player1['next']['left'] + Player1['next']['width'] * 0.3, 0)),
        'width': int(round(Player1['next']['width'] * 0.4, 0)),
        'height': int(round(Player1['next']['height'] * 0.1, 0))
    }
    Player2 = {
        'board': {'top': 115, 'left': 1194, 'width': 432, 'height': 805},
        'next': {'top': 115, 'left': 1094, 'width': 100, 'height': 200},
        'score': {'top': 930, 'left': 1194, 'width': 432, 'height': 100}
    }
    Player2['next_bit'] = {
        'top': int(round(Player2['next']['top'] + Player2['next']['height'] * 0.1, 0)),
        'left': int(round(Player2['next']['left'] + Player2['next']['width'] * 0.3, 0)),
        'width': int(round(Player2['next']['width'] * 0.5, 0)),
        'height': int(round(Player2['next']['height'] * 0.1, 0))
    }
    print('Player 1 Board: ' + str(Player1['board']))
    print('Player 1 NEXT: ' + str(Player1['next']))
    print('Player 2 Board: ' + str(Player2['board']))
    print('Player 2 NEXT: ' + str(Player2['next']))

    # Outline game areas for debugging purposes
    outline = Image.open(directory + '/img/calibration/outline.png')
    outline2 = Image.open(directory + '/img/calibration/outline2.png')
    outline = outline.resize((Player1['board']['width'], Player1['board']['height']))
    monitor.paste(outline, (Player1['board']['left'], Player1['board']['top']),
                                mask = outline)
    monitor.paste(outline, (Player2['board']['left'], Player2['board']['top']),
                                mask = outline)

    #Outline NEXT windows
    outline2 = outline2.resize((Player1['next']['width'], Player1['next']['height']))
    monitor.paste(outline2, (Player1['next']['left'], Player1['next']['top']), mask=outline2)
    monitor.paste(outline2, (Player2['next']['left'], Player2['next']['top']), mask=outline2)
    # Outline portion of NEXT windows used to infer placement timing.
    outline2 = outline2.resize((Player1['next_bit']['width'], Player1['next_bit']['height']))
    monitor.paste(outline2, (Player1['next_bit']['left'], Player1['next_bit']['top']), mask=outline2)
    monitor.paste(outline2, (Player2['next_bit']['left'], Player2['next_bit']['top']), mask=outline2)

    # Outline player scores. Maybe this'll get used later.
    outline = Image.open(directory + '/img/calibration/outline.png')
    # Player 1
    outline = outline.resize((Player1['score']['width'], Player1['score']['height']))
    monitor.paste(outline, (Player1['score']['left'], Player1['score']['top']),
                                mask = outline)
    monitor.paste(outline, (Player2['score']['left'], Player2['score']['top']),
                                mask = outline)

    # Board cell size.
    outline2 = Image.open(directory + '/img/calibration/outline2.png')
    cell_width = Player1['board']['width'] / 6
    cell_height = Player1['board']['height'] / 12
    print('Cell dimensions: ' + str((cell_width, cell_height)))  # Check for roundoff error
    cell_width = int(round(cell_width, 0))
    cell_height = int(round(cell_height, 0))
    outline2 = outline2.resize((cell_width, cell_height))

    for row in range(12):
        for col in range(6):
            monitor.paste(outline2, (Player1['board']['left'] + col * cell_width,
                                    Player1['board']['top'] + row * cell_height),
                                        mask = outline2)

    for row in range(12):
        for col in range(6):
            monitor.paste(outline2, (Player2['board']['left'] + col * cell_width,
                                    Player2['board']['top'] + row * cell_height),
                                        mask = outline2)

    print('Writing region outlines to /test/screen_regions.png')
    monitor.save(directory + '/test/screen_regions.png')


if __name__ == '__main__':
    monitor.show()