https://streamable.com/plh59

# PuyoSpectatorAssist
Creates an overlay that identifies potential chains

## Instructions
1. Whatever program you're using to capture Puyo Chronicle gameplay with, set it to full screen or get an estimate of its position on the screen.
2. Edit your screen regions at the top of calibrate_scrn.py
3. Modify your Puyo color calibration in calibrate_puyo.py (I didn't really comment/explain that part very well in the code yet...)
4. Run PuyoSpectatorAssist.py via command line
5. Use npm to install the package.json. Run a node.js server in the project directory using server.js
6. Add "localhost:3000" as a 1920x1080 browser source in OBS. Scale it to fit the canvas if you have to.

## ToDo
* Add detection for NEXT Window movement so the prediction is only generated in-between moves. It makes the overlay less distracting.
* Improve accuracy of Puyo detection with OpenCV(?) somehow(?). Pre-process the player fields with some sort of thresholding, or something else fancy with OpenCV. Currently, the script will sometimes mistake the character backgrounds as Puyos.
* Define pre-set settings for Puyo Puyo Tetris.
* Actually learn how node and javascript works so I actually understand how server.js works lol. Right now it's just using template code I found somewhere else: https://github.com/yanalavishnu/imgstream
