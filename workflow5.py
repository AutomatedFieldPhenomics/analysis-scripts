#!/usr/bin/env python3

#-----------------------------------------------------------------------------
# 	This workflow script was made to analyze plant images taken in the
# visible spectrum. More specifically the threshold values were adjusted were
# adjusted to analyze a specific rhubarb plant in a garden.
#-----------------------------------------------------------------------------

import argparse
import sys
import os
import numpy as np
import cv2
import matplotlib
from plantcv import plantcv as pcv

def options():
    parser = argparse.ArgumentParser(description="Imaging processing with opencv")
    parser.add_argument("-i", "--image", help="Input image file.", required=True)
    parser.add_argument("-r", "--result", help="Result file.", required=True)
    parser.add_argument("-o", "--outdir", help="Output directory for image files.", required=False)
    parser.add_argument("-w", "--writeimg", help="Write out images.", default=False, action="store_true")
    parser.add_argument("-D", "--debug", help="Turn on debug, prints intermediate images.")
    args = parser.parse_args()
    return args

def main():
    # Get options
    args = options()

    # Set variables
    device = 0
    pcv.params.debug = args.debug
    img_file = args.image

    # Read image
    img, path, filename = pcv.readimage(filename=img_file, mode='rgb') 

    # Process saturation channel from HSV colour space
    s = pcv.rgb2gray_hsv(rgb_img=img, channel='s')
    lp_s = pcv.laplace_filter(s, 1, 1)
    shrp_s = pcv.image_subtract(s, lp_s)
    s_eq = pcv.hist_equalization(shrp_s)
    s_thresh = pcv.threshold.binary(gray_img=s_eq, threshold=215, max_value=255, object_type='light')
    s_mblur = pcv.median_blur(gray_img=s_thresh, ksize=5)

    # Process green-magenta channel from LAB colour space
    b = pcv.rgb2gray_lab(rgb_img=img, channel='a')
    b_lp   = pcv.laplace_filter(b, 1, 1)
    b_shrp = pcv.image_subtract(b, b_lp)
    b_thresh = pcv.threshold.otsu(b_shrp, 255, object_type='dark')

    # Create and apply mask
    bs = pcv.logical_or(bin_img1=s_mblur, bin_img2=b_thresh)
    filled = pcv.fill_holes(bs)
    masked = pcv.apply_mask(img=img, mask=filled, mask_color='white')

    # Extract colour channels from masked image
    masked_a = pcv.rgb2gray_lab(rgb_img=masked, channel='a')
    masked_b = pcv.rgb2gray_lab(rgb_img=masked, channel='b')

    # Threshold the green-magenta and blue images
    maskeda_thresh = pcv.threshold.binary(gray_img=masked_a, threshold=115, 
                                            max_value=255, object_type='dark')
    maskeda_thresh1 = pcv.threshold.binary(gray_img=masked_a, threshold=140, 
                                            max_value=255, object_type='light')
    maskedb_thresh = pcv.threshold.binary(gray_img=masked_b, threshold=128, 
                                            max_value=255, object_type='light')

    # Join the thresholded saturation and blue-yellow images (OR)
    ab1 = pcv.logical_or(bin_img1=maskeda_thresh, bin_img2=maskedb_thresh)
    ab = pcv.logical_or(bin_img1=maskeda_thresh1, bin_img2=ab1)

    # Produce and apply a mask
    opened_ab = pcv.opening(gray_img=ab)
    ab_fill = pcv.fill(bin_img=ab, size=200)
    closed_ab = pcv.closing(gray_img=ab_fill)
    masked2 = pcv.apply_mask(img=masked, mask=bs, mask_color='white')

    # Identify objects
    id_objects, obj_hierarchy = pcv.find_objects(img=masked2, mask=ab_fill)

    # Define region of interest (ROI)
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked2, x=250, y=100, h=200, w=200)

    # Decide what objects to keep
    roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                               roi_hierarchy=roi_hierarchy, 
                                                               object_contour=id_objects, 
                                                               obj_hierarchy=obj_hierarchy,
                                                               roi_type='partial')

    # Object combine kept objects
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)

    ############### Analysis ################ 

    outfile=False
    if args.writeimg == True:
        outfile = args.outdir + "/" + filename
        
    # Analyze the plant
    analysis_image = pcv.analyze_object(img=img, obj=obj, mask=mask)
    color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')
    top_x, bottom_x, center_v_x = pcv.x_axis_pseudolandmarks(img=img, obj=obj, mask=mask)
    top_y, bottom_y, center_v_y = pcv.y_axis_pseudolandmarks(img=img, obj=obj, mask=mask)

    # Print results of the analysis
    pcv.print_results(filename=args.result)
    pcv.output_mask(img, kept_mask, filename, outdir=args.outdir, mask_only=True)

if __name__ == '__main__':
    main()
