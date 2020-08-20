#!/usr/bin/env python3
# coding: utf-8

#------------------------------------------------
#   This script can be used as a tool for visualizing the movement of a plant
# over a series of images after they have already been masked. Every file in a
# given directory is iterated over and compared with the output of the previous
# comparision.
#------------------------------------------------

import os
from plantcv import plantcv as pcv
import numpy as np
import cv2
import argparse

def options():
    parser = argparse.ArgumentParser(description="Mask overlay")
    parser.add_argument('-d', '--directory', help="Input directory of binary
                            images", requried=True)
    parser.add_argument('-c', '--colourChange', help='Colour change between
                            layers', default=10, required=False)
    parser.add_argument('-o', '--outputFile', help='File to output mask overlay',
                            default='Mask_Overlay.png')
    args = parser.parse_args()
    return args

#------------------------------------------------
# Adds a layer to single image comprised of overlapped masks in different
# colours
#------------------------------------------------
def addLayer(file1, file2, num, colourfile):
    file3 = cv2.bitwise_xor(file1,file2)
    rows, cols, colour = file3.shape
    for i in range(rows):
        for j in range(cols):
            if file3[i,j,2] >= 20:
                colourfile[i,j] = [num,1.1*num,1.2*num]
    return colourfile 

#------------------------------------------------
# Creates the base layer of the image overlay
#------------------------------------------------
def baseLayer(file1, colourfile):
    rows, cols, colour = file1.shape
    for i in range(rows):
        for j in range(cols):
            if file1[i,j,2] >= 20:
                colourfile[i,j] = [100,100,0]
    return colourfile 

def main():
    
    # Get arguments
    args = options()
    myfolder = args.directory
    num = args.colourChange

    count = 0
    colourfile = np.zeros((720,480,3), np.uint8)
    for file in sorted(os.listdir(myfolder), reverse=True):
        path2file = '{a}/{b}'.format(a=myfolder,b=file)
        if file != '.DS_Store' and file != '.ipynb_checkpoints':
            count +=1
            num += 3
            file1 = cv2.imread(path2file)
            if count == 1:
                #colour the base layer
                colourfile = baseLayer(file1, colourfile)
            if count > 1:
                # anything that was not in the last image gets added to the new image in a new colour
                colourfile = addLayer(file1,file2, num, colourfile)
            file2 = file1
    cv2.imwrite(args.outputFile, colourfile) 

if __name__ == '__main__':
    main()
