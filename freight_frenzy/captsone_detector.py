import cv2 as cv
import numpy as np
from time import sleep
import keyboard


class CapstoneDetector:
    def __init__(self, filename) -> None:
        self.image = cv.imread(filename)
        self.hls = None
    
    def image_prep(self):
        resized = cv.resize(self.image, (800,400))
        self.image = resized
        blurred = cv.blur(resized, (5,5))
        self.hls = cv.cvtColor(blurred, cv.COLOR_RGB2HSV)
        cv.imshow('Cvt Color', self.image)
        pass
        
    def find_contours(self):
        # lower_range_h = 0
        # lower_range_s = 0
        # lower_range_v = 0
        # upper_range_h = 0
        # upper_range_s = 0
        # upper_range_v = 0
        # while 1:
        #     if keyboard.is_pressed('q'):
        #         lower_range_h += 1
        #     if keyboard.is_pressed('a'):
        #         lower_range_h -= 1
        #     if keyboard.is_pressed('w'):
        #         lower_range_s += 1
        #     if keyboard.is_pressed('s'):
        #         lower_range_s -= 1
        #     if keyboard.is_pressed('e'):
        #         lower_range_v += 1
        #     if keyboard.is_pressed('d'):
        #         lower_range_v -= 1
        #     if keyboard.is_pressed('u'):
        #         upper_range_h += 1
        #     if keyboard.is_pressed('j'):
        #         upper_range_h -= 1
        #     if keyboard.is_pressed('i'):
        #         upper_range_s += 1
        #     if keyboard.is_pressed('k'):
        #         upper_range_s -= 1
        #     if keyboard.is_pressed('o'):
        #         upper_range_v += 1
        #     if keyboard.is_pressed('l'):
        #         upper_range_v -= 1
        #     print(f"Lower Range H: {lower_range_h}, Lower Range S: {lower_range_s}, Lower Range V: {lower_range_v}, Upper Range H: {upper_range_h}, Upper Range S: {upper_range_s}, Upper Range V {upper_range_v}")
        #     break
        lower_range = np.array([30,60,8]) # 8
        upper_range = np.array([90,90,35]) # 35
        mask = cv.inRange(self.image, lower_range, upper_range)
        cv.imshow('Masked', mask)
        sleep(0.5)
        cv.waitKey(0)

        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        areas = list(map(lambda contour: cv.contourArea(contour), contours))
        contour_id = areas.index(max(areas))
        cv.drawContours(self.image, contours, contour_id, (0, 255, 0), 1)
        cv.imshow('Drawn', self.image)

        cv.setMouseCallback('Drawn', lambda event, x, y, flags, param: print(x, y) if event == cv.EVENT_LBUTTONDOWN else None)
        cv.waitKey(0)
        