import cv2
import subprocess as sp
import numpy as np
from funcs import get_rect_grid_coords, get_chess_grid_coords, create_ellipse_mask

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



class Stream:
    '''
    black_and_white_effect - 0
    hsv - 1
    chess_effect - 2
    ellipse - 3
    '''

    active_effects = np.array([], dtype=np.uint8)
    curr_width = 0
    curr_height = 0
    raw_frame_height = 0
    raw_frame_width = 0
    width_resize_factor = None
    height_resize_factor = None
    chess_coord_list = None
    chess_mask = None
    ellipse_mask = None

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
        frame = np.fromstring(frame, dtype='uint8').reshape((730,1296,3))
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
        for effect in np.nditer(self.active_effects):
            if effect == 0:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if effect == 1:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            if effect == 2:
                frame = self.apply_chess_filter_to_frame(frame)
            if effect == 3:
                frame = self.apply_ellipse_filter_to_frame(frame)
        return frame


    def apply_chess_filter_to_frame(self, frame):
        # if frame.ndim < 3:
        #     frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blured = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(gray, 0, 30)
        edges_3d = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_3d[np.logical_or(edges_3d, 0)] = 1
        edges_3d*=np.uint8([255,171,0])
        edges_3d = cv2.GaussianBlur(edges_3d, (5,5), 0)

        inverted_mask = cv2.bitwise_not(self.chess_mask)
        frame_with_effects = edges_3d
        overlay_with_effects = cv2.bitwise_and(frame_with_effects, frame_with_effects, mask = self.chess_mask)
        frame_with_blackout = cv2.bitwise_and(frame, frame, mask = inverted_mask)

        return cv2.add(frame_with_blackout, overlay_with_effects)

    def get_frame(self, raw_frame):
        frame = self.raw_frame_handle(raw_frame)
        if frame is not None:
            if len(self.active_effects) > 0:
                frame = self.aply_effects(frame)
            # cv2.imshow('stream', frame)
        # ret, jpg = cv2.imencode('.jpg', frame)

        # print(ret)
        return frame


    def apply_ellipse_filter_to_frame(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # blured = cv2.GaussianBlur(gray, (5,5), 0)
        # edges = cv2.Canny(gray, 0, 30)
        # edges_3d = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        # edges_3d[np.logical_or(edges_3d, 0)] = 1
        # edges_3d*=np.uint8([255,171,0])
        # edges_3d = cv2.GaussianBlur(edges_3d, (5,5), 0)

        frame_with_effects = hsv

        inverted_mask = cv2.bitwise_not(self.ellipse_mask)

        overlay_with_effects = cv2.bitwise_and(frame_with_effects, frame_with_effects, mask = self.ellipse_mask)
        frame_with_blackout = cv2.bitwise_and(frame, frame, mask = inverted_mask)

        return cv2.add(frame_with_blackout, overlay_with_effects)

    def black_and_white(self):
        self.active_effects = np.append(self.active_effects, 0)
        return self

    def hsv(self):
        self.active_effects = np.append(self.active_effects, 1)
        return self

    def chess(self, chess_side_length):
        if self.chess_mask is None:
            self.chess_mask = self.create_chessboard_mask(self.curr_width, self.curr_height, chess_side_length)
        self.active_effects = np.append(self.active_effects, 2)
        return self

    def ellipse(self):
        if self.ellipse_mask == None:
            self.ellipse_mask = create_ellipse_mask(self.curr_width, self.curr_height, False)
        self.active_effects = np.append(self.active_effects, 3)
        return self




# stream = Stream(input_frame_width = 1296, input_frame_height = 730)
# stream.set_resolution(width = 1296, height = 730)
# stream.ellipse()

#
# while True:
#     frame = stream.get_frame(pipe.stdout.read(1296*730*3))
#     if frame is not None:
#         cv2.imshow('Video', frame)
#         cv2.imwrite('AAA.jpg', frame)
#     if cv2.waitKey(500) & 0xFF == ord('q'):
#         break
#     pipe.stdout.flush()
#
# cv2.destroyAllWindows()
