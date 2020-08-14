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

    # Get options
    args = options()

    # Set debug to the global parameter 
    pcv.params.debug = args.debug

    # Inputs:
    #   filename - Image file to be read in 
    #   mode - How to read in the image; either 'native' (default), 'rgb', 'gray', or 'csv'
    img, path, filename = pcv.readimage(filename=args.image)
    # rotate the image
    img = pcv.rotate(img, -90, False)
    # Convert RGB to LAB and extract the blue channel ('b')

    # Input:
    #   rgb_img - RGB image data 
    #   channel- Split by 'l' (lightness), 'a' (green-magenta), or 'b' (blue-yellow) channel
    l = pcv.rgb2gray_lab(rgb_img=img, channel='b')

    # Take a binary threshold to separate plant from background. 
    # Threshold can be on either light or dark objects in the image. 

    # Inputs:
    #   gray_img - Grayscale image data 
    #   threshold- Threshold value (between 0-255)
    #   max_value - Value to apply above threshold (255 = white) 
    #   object_type - 'light' (default) or 'dark'. If the object is lighter than 
    #                 the background then standard threshold is done. If the object 
    #                 is darker than the background then inverse thresholding is done. 
    # Threshold the blue channel image 
    l_thresh = pcv.threshold.binary(gray_img=l, threshold=115, max_value=255, 
                                    object_type='dark')

    # Median Blur to clean noise 

    # Inputs: 
    #   gray_img - Grayscale image data 
    #   ksize - Kernel size (integer or tuple), (ksize, ksize) box if integer input,
    #           (n, m) box if tuple input 
    l_mblur = pcv.median_blur(gray_img=l_thresh, ksize=5)

  
    # Appy Mask (for VIS images, mask_color='white')

    # Inputs:
    #   img - RGB or grayscale image data 
    #   mask - Binary mask image data 
    #   mask_color - 'white' or 'black' 
    masked = pcv.apply_mask(img=img, mask=l_mblur, mask_color='white')

    # Fill small objects (reduce image noise) 

    # Inputs: 
    #   bin_img - Binary image data 
    #   size - Minimum object area size in pixels (must be an integer), and smaller objects will be filled
    ab_fill = pcv.fill(bin_img=l_mblur, size=50)

    # Identify objects

    # Inputs: 
    #   img - RGB or grayscale image data for plotting 
    #   mask - Binary mask used for detecting contours 
    id_objects, obj_hierarchy = pcv.find_objects(img=img, mask=ab_fill)

    # Define the region of interest (ROI) 

    # Inputs: 
    #   img - RGB or grayscale image to plot the ROI on 
    #   x - The x-coordinate of the upper left corner of the rectangle 
    #   y - The y-coordinate of the upper left corner of the rectangle 
    #   h - The height of the rectangle 
    #   w - The width of the rectangle 
    roi1, roi_hierarchy= pcv.roi.rectangle(img=masked, x=150, y=270, h=100, w=100)

    # Decide which objects to keep

    # Inputs:
    #    img            = img to display kept objects
    #    roi_contour    = contour of roi, output from any ROI function
    #    roi_hierarchy  = contour of roi, output from any ROI function
    #    object_contour = contours of objects, output from pcv.find_objects function
    #    obj_hierarchy  = hierarchy of objects, output from pcv.find_objects function
    #    roi_type       = 'partial' (default, for partially inside the ROI), 'cutto', or 
    #                     'largest' (keep only largest contour)
    roi_objects, hierarchy3, kept_mask, obj_area = pcv.roi_objects(img=img, roi_contour=roi1, 
                                                                   roi_hierarchy=roi_hierarchy, 
                                                                   object_contour=id_objects, 
                                                                   obj_hierarchy=obj_hierarchy,
                                                                   roi_type='partial')

    # Object combine kept objects

    # Inputs:
    #   img - RGB or grayscale image data for plotting 
    #   contours - Contour list 
    #   hierarchy - Contour hierarchy array 
    obj, mask = pcv.object_composition(img=img, contours=roi_objects, hierarchy=hierarchy3)

    ############### Analysis ################ 

    # Find shape properties, data gets stored to an Outputs class automatically

    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj- Single or grouped contour object
    #   mask - Binary image mask to use as mask for moments analysis 
    analysis_image = pcv.analyze_object(img=img, obj=obj, mask=mask)

    # Shape properties relative to user boundary line (optional)

    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj - Single or grouped contour object 
    #   mask - Binary mask of selected contours 
    #   line_position - Position of boundary line (a value of 0 would draw a line 
    #                   through the bottom of the image) 
    boundary_image2 = pcv.analyze_bound_horizontal(img=img, obj=obj, mask=mask, 
                                                   line_position=370)

    # Determine color properties: Histograms, Color Slices and Pseudocolored Images, output color analyzed images (optional)

    # Inputs:
    #   rgb_img - RGB image data
    #   mask - Binary mask of selected contours 
    #   hist_plot_type - None (default), 'all', 'rgb', 'lab', or 'hsv'
    #                    This is the data to be printed to the SVG histogram file  
    color_histogram = pcv.analyze_color(rgb_img=img, mask=kept_mask, hist_plot_type='all')

    # Print the histogram out to save it 
    pcv.print_image(img=color_histogram, filename='{}_color_hist.jpg'.format(args.outdir))

    # Divide plant object into twenty equidistant bins and assign pseudolandmark points based upon their 
    # actual (not scaled) position. Once this data is scaled this approach may provide some information 
    # regarding shape independent of size.

    # Inputs:
    #   img - RGB or grayscale image data 
    #   obj - Single or grouped contour object 
    #   mask - Binary mask of selected contours 
    top_x, bottom_x, center_v_x = pcv.x_axis_pseudolandmarks(img=img, obj=obj, mask=mask)

    top_y, bottom_y, center_v_y = pcv.y_axis_pseudolandmarks(img=img, obj=obj, mask=mask)

    # The print_results function will take the measurements stored when running any (or all) of these functions, format, 
    # and print an output text file for data analysis. The Outputs class stores data whenever any of the following functions
    # are ran: analyze_bound_horizontal, analyze_bound_vertical, analyze_color, analyze_nir_intensity, analyze_object, 
    # fluor_fvfm, report_size_marker_area, watershed. If no functions have been run, it will print an empty text file 
    pcv.print_results(filename='{}'.format(args.result))



    # Print the mask out to save it 
    pcv.print_image(img=kept_mask, filename='{}_mask.jpg'.format(args.outdir))
 
    
if __name__ == "__main__":
        main()