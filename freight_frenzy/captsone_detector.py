import cv2 as cv
import numpy as np


class CapstoneDetector:
    def __init__(self, filename) -> None:
        self.image = cv.imread(filename)
        self.hls = None
    
    def image_prep(self):
        # resized = cv.resize(self.image, (800,400))
        # self.image = resized
        # blurred = cv.blur(resized, (5,5))
        # cv.imshow('Blurred', blurred)
        # self.hls = cv.cvtColor(blurred, cv.COLOR_BGR2HLS)
        # cv.imshow('Cvt Color', self.image)
        pass
    
    def find_contours(self):
        lower_range = np.array([40,110,0])
        upper_range = np.array([60,130,255])
        mask = cv.inRange(self.image, lower_range, upper_range)
        cv.imshow('Masked', mask)

        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        areas = list(map(lambda contour: cv.contourArea(contour), contours))
        contour_id = areas.index(max(areas))
        cv.drawContours(self.image, contours, contour_id, (0, 255, 0), 1)
        cv.imshow('Drawn', self.image)

        cv.setMouseCallback('Drawn', lambda event, x, y, flags, param: print(x, y) if event == cv.EVENT_LBUTTONDOWN else None)
        cv.waitKey(0)
        