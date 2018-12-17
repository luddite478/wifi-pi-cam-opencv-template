import cv2
import subprocess as sp
import numpy as np
from funcs import get_rect_grid_coords, get_chess_grid_coords

'''
Notes:
1. x,y order:
    image.shape -> (y,x)
    np.zeros((y,x))
    opencv point coords -> (x,y)

2. cv2.fillPoly should recirve np.int32 array reshaped to (-1,1,2)
   dtypes should always match for array operations

TODO:
    fix setup without set_resolution
'''

FFMPEG_BIN = "ffmpeg"
command = [ FFMPEG_BIN,
        '-i', 'fifo264',          # fifo is the named pipe
        '-pix_fmt', 'bgr24',      # opencv requires bgr24 pixel format.
        '-vcodec', 'rawvideo',
        '-an','-sn',              # we want to disable audio processing (there is no audio)
        '-f', 'image2pipe', '-' ]
pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)

class Stream:
    active_effects = []
    curr_width = 0
    curr_height = 0
    raw_frame_height = 0
    raw_frame_width = 0
    width_resize_factor = None
    height_resize_factor = None
    chess_coord_list = None
    chess_mask = None

    def __init__(self, input_frame_width, input_frame_height):
        self.raw_frame_width = input_frame_width
        self.raw_frame_height = input_frame_height

    def create_chessboard_mask(self, imgW, imgH, chess_side_len):
        black_image = np.full((imgH, imgW), 255, dtype = np.uint8)
        return self.drawChessBoard(black_image, chess_side_len)

    def drawChessBoard(self, frame, chess_side_len):
        if self.chess_coord_list is None:
            self.chess_coord_list = get_chess_grid_coords(frame, chess_side_len, indent=False)
        for i in range(0, len(self.chess_coord_list), 4):
            squareCoords = [self.chess_coord_list[i], self.chess_coord_list[i+1], self.chess_coord_list[i+2], self.chess_coord_list[i+3]]
            numpySquareCoords = np.int32(squareCoords).reshape(-1,1,2)
            cv2.fillPoly(frame, [numpySquareCoords], (0,0,0))
        return frame

    def raw_frame_handle(self, frame):
        frame = np.fromstring(frame, dtype='uint8').reshape((480,640,3))
        if self.width_resize_factor is not None or self.height_resize_factor is not None:
            frame = self.resize(frame)
        return frame

    def set_resolution(self, width, height):
        self.curr_width = width
        self.curr_height = height
        self.width_resize_factor =  width/self.raw_frame_width
        self.height_resize_factor = height/self.raw_frame_height

    def resize(self, frame):
        return cv2.resize(frame, (0,0), fx = self.width_resize_factor, fy = self.height_resize_factor)

    def aply_effects(self, frame):
        for effect in self.active_effects:
            if effect is 'chess':
                inverted_mask = cv2.bitwise_not(self.chess_mask)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blured = cv2.GaussianBlur(gray, (5,5), 0)
                edges = cv2.Canny(blured, 50, 200)
                edges_3d = np.repeat(edges[:, :, np.newaxis], 3, axis=2)
                edges_3d[np.where((edges_3d==[255,255,255]).all(axis=2))] = [255,171,0]
                blured2 = cv2.GaussianBlur(edges_3d, (5,5), 0)
                frame_with_effects = blured2
                overlay_with_effects = cv2.bitwise_and(frame_with_effects, frame_with_effects, mask = inverted_mask)
                frame_with_blackout = cv2.bitwise_and(frame, frame, mask = self.chess_mask)

                result = cv2.add(frame_with_blackout, overlay_with_effects)
                blured2 = cv2.GaussianBlur(result, (5,5), 0)
        return blured2

    def play(self, raw_frame):
        frame = self.raw_frame_handle(raw_frame)
        if frame is not None:
            if len(self.active_effects) > 0:
                frame = self.aply_effects(frame)
            cv2.imshow('stream', frame)

    def turn_on_chess(self, chess_side_length):
        if self.chess_mask is None:
            self.chess_mask = self.create_chessboard_mask(self.curr_width, self.curr_height, chess_side_length)
        self.active_effects.append('chess')

stream = Stream(input_frame_width = 640, input_frame_height = 480)
stream.set_resolution(width = 640, height = 480)
stream.turn_on_chess(7)
while True:
    stream.play(pipe.stdout.read(640*480*3))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    pipe.stdout.flush()

cv2.destroyAllWindows()
