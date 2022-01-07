from typing import List
import cv2 as cv
import numpy as np
from time import sleep
from pynput.keyboard import Key, Listener
from sys import exit


class CapstoneDetector:
    def __init__(self, filename) -> None:
        self.image = cv.imread(filename)
        self.hls = None

    def image_prep(self):
        # cv.imshow('Original', self.image)
        resized = cv.resize(self.image, (800,400))
        blurred = cv.blur(resized, (5,5))
        # cv.imshow('Blur', blurred)
        rgb = cv.cvtColor(blurred, cv.COLOR_BGR2RGB)
        self.image = rgb

    def find_color_ranges(self):
        wnd = 'Colorbars'
        cv.namedWindow(wnd)

        def nothing(x):
            pass

        rsl='Red Low'
        rsh='Red High'
        gsl='Green Low'
        gsh='Green High'
        bsl='Blue Low'
        bsh='Blue High'
        cv.createTrackbar(rsl, wnd,0,255,nothing)
        cv.createTrackbar(rsh, wnd,0,255,nothing)
        cv.createTrackbar(gsl, wnd,0,255,nothing)
        cv.createTrackbar(gsh, wnd,0,255,nothing)
        cv.createTrackbar(bsl, wnd,0,255,nothing)
        cv.createTrackbar(bsh, wnd,0,255,nothing)

        while 1:
            rvl = cv.getTrackbarPos(rsl, wnd)
            rvh = cv.getTrackbarPos(rsh, wnd)
            gvl = cv.getTrackbarPos(gsl, wnd)
            gvh = cv.getTrackbarPos(gsh, wnd)
            bvl = cv.getTrackbarPos(bsl, wnd)
            bvh = cv.getTrackbarPos(bsh, wnd)

            lower_range = np.array([rvl,gvl,bvl])
            upper_range = np.array([rvh,gvh,bvh])
            mask = cv.inRange(self.image, lower_range, upper_range)

            cv.imshow('Colorbars', mask)
            key = cv.waitKey(1)

    def masked(self):
        lower_range = np.array([96,121,48])
        upper_range = np.array([132,155,98])
        mask = cv.inRange(self.image, lower_range, upper_range)
        cv.imshow('Masked', mask)
        cv.waitKey(0)


    def draw_contours(self):
        contours, _ = cv.findContours(mask, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        areas = list(map(lambda contour: cv.contourArea(contour), contours))
        contour_id = areas.index(max(areas))
        cv.drawContours(self.image, contours, contour_id, (0, 255, 0), 1)
        cv.imshow('Drawn', self.image)
        cv.waitKey(0)
