#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 15:31:17 2020

@author: arloreichert
"""

# Import Libraries 
from plantcv import plantcv as pcv
import argparse

def options():
    parser = argparse.ArgumentParser(description="Imaging processing with opencv")
    parser.add_argument("-i", "--image", help="Input image file.", required=True)
    parser.add_argument("-r", "--result", help="Result file.", required=True)
    parser.add_argument("-o", "--outdir", help="Output directory for image files.", required=False)
    parser.add_argument("-w", "--writeimg", help="Write out images.", default=False, action="store_true")
    parser.add_argument("-D", "--debug", help="Turn on debug, prints intermediate images.")
    args = parser.parse_args()
    return args

# main pipeline to perform pcv functions and save files
def main():

    # Set variables
    args = options()
    pcv.params.debug = args.debug

    # Read and rotate image
    img, path, filename = pcv.readimage(filename=args.image)
    img = pcv.rotate(img, -90, False)

    # Create mask from LAB b channel
    l = pcv.rgb2gray_lab(rgb_img=img, channel='b')
    l_thresh = pcv.threshold.binary(gray_img=l, threshold=115, max_value=255, 
                                    object_type='dark')
    l_mblur = pcv.median_blur(gray_img=l_thresh, ksize=5)

    # Apply mask to image 
    masked = pcv.apply_mask(img=img, mask=l_mblur, mask_color='white')
    ab_fill = pcv.fill(bin_img=l_mblur, size=50)

    # Extract plant object from image
    id_objects, obj_hierarchy = pcv.find_objects(img=img, mask=ab_fill)
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked, x=150, y=270, h=100, w=100)
    roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                                   roi_hierarchy=roi_hierarchy, 
                                                                   object_contour=id_objects, 
                                                                   obj_hierarchy=obj_hierarchy,
                                                                   roi_type='partial')
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)

    ############### Analysis ################ 

    # Analyze shape properties
    analysis_image = pcv.analyze_object(img=img, obj=obj, mask=mask)
    boundary_image2 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, 
                                                   line_position=370)

    # Analyze colour properties
    color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')

    # Analyze shape independent of size
    top_x, bottom_x, center_v_x = pcv.x_axis_pseudolandmarks(img=img, obj=obj, mask=mask)
    top_y, bottom_y, center_v_y = pcv.y_axis_pseudolandmarks(img=img, obj=obj, mask=mask)

    # Print results
    pcv.print_results(filename='{}'.format(args.result))
    pcv.print_image(img=color_histogram, filename='{}_color_hist.jpg'.format(args.outdir))
    pcv.print_image(img=kept_mask, filename='{}_mask.jpg'.format(args.outdir))
 
    
if __name__ == "__main__":
        main()
