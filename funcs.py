import numpy as np
import cv2

def get_thresh_edge_vals(img):
    med_val = np.median(img)
    lower = int(max(0,0.7*med_val))
    upper = int(min(255,1.3*med_val))
    return lower, upper


# def gamma_incr(img):
#     lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
#     l, a, b = cv2.split(lab)
#
#     #Applying CLAHE to L-channel
#     clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(2,2))
#     cl = clahe.apply(l)
#
#     #Merge the CLAHE enhanced L-channel with the a and b channel
#     limg = cv2.merge((cl,a,b))
#
#     #Converting image from LAB Color model to RGB model
#     final = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    # return final

# def draw_line(frame):
#     rho = 1  # distance resolution in pixels of the Hough grid
#     theta = np.pi / 180  # angular resolution in radians of the Hough grid
#     threshold = 15  # minimum number of votes (intersections in Hough grid cell)
#     min_line_length = 150  # minimum number of pixels making up a line
#     max_line_gap = 20  # maximum gap in pixels between connectable line segments
#     line_image = np.copy(image) * 0  # creating a blank to draw lines on
#     lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
#     for line in lines:
#         for x1,y1,x2,y2 in line:
#             cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)
#
#     return cv2.addWeighted(image, 0.8, line_image, 1, 0)


def get_chess_grid_coords(img, number_of_rects, *args, **kwargs):
    if len(args) >= 2:
        h, w = args[0], args[1]
    else:
        h, w = img.shape[0], img.shape[1]
        
    print(kwargs)
    if 'indent' in kwargs and kwargs.get('indent') == False:
        x_Arr = np.linspace(0, w, num = number_of_rects+3, dtype=np.uint16)
        y_Arr = np.linspace(0, h, num = number_of_rects+3, dtype=np.uint16)
    else:
        x_Arr = np.linspace(0, w, num = number_of_rects+3, dtype=np.uint16)[1:-1]
        y_Arr = np.linspace(0, h, num = number_of_rects+3, dtype=np.uint16)[1:-1]

    coord_list = []
    for i in range(len(y_Arr)-1):
        for j in range(len(x_Arr)-1):
            if j%2 == 1 and i%2 == 1:
                coord_list.append([x_Arr[j], y_Arr[i]])
                coord_list.append([x_Arr[j+1], y_Arr[i]])
                coord_list.append([x_Arr[j+1], y_Arr[i+1]])
                coord_list.append([x_Arr[j], y_Arr[i+1]])
            elif j%2 == 0 and i%2 == 0:
                coord_list.append([x_Arr[j], y_Arr[i]])
                coord_list.append([x_Arr[j+1], y_Arr[i]])
                coord_list.append([x_Arr[j+1], y_Arr[i+1]])
                coord_list.append([x_Arr[j], y_Arr[i+1]])
    # print(coord_list)
    # res = np.array(coord_list).reshape(-1,1,2)
    return coord_list

def get_rect_grid_coords(img, number_of_rects, *args):
    if len(args) >= 2:
        h, w = args[0], args[1]
    else:
        h, w = img.shape[1], img.shape[0]

    x_Arr = np.linspace(0, h, num = number_of_rects+3, dtype=np.uint16)[1:-1]
    y_Arr = np.linspace(0, w, num = number_of_rects+3, dtype=np.uint16)[1:-1]

    coord_list = []
    # print(len(x_Arr)-1)
    for i in range(len(y_Arr)-1):
        for j in range(len(x_Arr)-1):
            coord_list.append([(x_Arr[j], y_Arr[i]), (x_Arr[j+1], y_Arr[i+1])])

    return coord_list


# img = cv2.imread('2.jpg')
#
# points2 = get_polygon_grid_coords(img, 80)
# for pair in list:
#     cv2.rectangle(img,pair[0],pair[1],(0,0,255), 2)

# while True:
    # cv2.fillPoly(img, [], (255,0,0))
# print(len(points2))
# for i in range(0, len(points2), 4):
#     xx = [points2[i], points2[i+1], points2[i+2], points2[i+3]]
#     yy = np.array(xx, dtype=np.int32).reshape(-1,1,2)
#
#     cv2.fillPoly(img, [yy], (255,0,0))
#
# cv2.imshow('Videoa', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# if cv2.waitKey(1) & 0xFF == ord('q'):
