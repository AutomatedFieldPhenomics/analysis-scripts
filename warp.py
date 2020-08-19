#!/usr/bin/env python3

#-----------------------------------------------------------------------------
# 	Using a given image and homography matrix this script warps the 
# original image and outputs the warped image
#-----------------------------------------------------------------------------

import argparse
import cv2
from plantcv import plantcv as pcv
import numpy as np

def options():
    parser = argparse.ArgumentParser(description="Imaging processing with opencv")
    parser.add_argument("-i", "--image", help="Input image file.", required=True)
    parser.add_argument("-o", "--outdir", help="Output directory for image files.", required=False)
    parser.add_argument("-m", "--matrix", help="Homography matrix for warping images.", required=True)
    args = parser.parse_args()
    return args

def main():
    args = options()
    
    h = np.load(args.matrix)

    srcIm, path, filename = pcv.readimage(args.image, 'rgb')
    
    height, width, channels = srcIm.shape
    dstIm = cv2.warpPerspective(srcIm, h, (width, height))
    
    destination = args.outdir + '/' + filename
    cv2.imwrite(destination, dstIm)

if __name__ == '__main__':
    main()
