from plantcv import plantcv as pcv
import numpy as np
import cv2

class options:
    def __init__(self):
        self.debug = "plot"
        self.writeimg= False


args = options()
 
pcv.params.debug = args.debug

# Path of the VIS image to be read in 
vis_filename = ''

# Read in the ndvi mask and corresponding VIS image
mask, mask_path, mask_filename = pcv.readimage('ndvi_mask.png')
vis, vis_path, vis_filename = pcv.readimage(vis_filename)

# Align the VIS image to the mask using the homography matrix calculated in homography_gui_activity.py
h = np.loadtxt('h_matrix.csv', delimiter=',')
aligned = cv2.warpPerspective(vis, h, (vis.shape[1], vis.shape[0]))

# Use the NDVI mask to mask the VIS image
img = pcv.apply_mask(aligned, mask, 'white')



# Load in the colours that the you have declared are to be removed
rm_colours = np.loadtxt('rm_colours.csv', delimiter=',')
rm_list = []
for colour in rm_colours:
    rm_list.append(colour)
    
# Load in the colours that you have declared are to be kept
keep_colours = np.loadtxt('keep_colours.csv', delimiter=',')
keep_list = []
for colour in keep_colours:
    keep_list.append(colour)
    

#-------------------------------------------------------------------------------------------------#
# We will compare each pixel's RGB values to those of the colours that were loaded in above. If all three 
# colour channel values are no more than rm_perc% larger or smaller than those in any of the colours in
# rm_list, the pixel will be removed from the final mask. Similarly, if all three colour channel values
# are more than keep_perc% larger or smaller than those in any of the colours in keep_list, the pixel will
# be removed from the final mask.
#-------------------------------------------------------------------------------------------------#
keep_perc = 35
rm_perc = 10

filtered = img.copy()
for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            
            pixel = img[y, x]
            
            if np.all(pixel) != 255:
                
                pixel[pixel == 0] = 1
                
                keep_fracs = []
                for colour in keep_list:
                    keep_fracs.append(colour/pixel)
                
                rm_fracs = []
                for colour in rm_list:
                    rm_fracs.append(colour/pixel)
                    
                
                keep_match = False
                rm_match = False
                
                for frac in keep_fracs:
                    if np.abs((frac[0] - 1) * 100) <= keep_perc:
                        if np.abs((frac[1] - 1) * 100) <= keep_perc:
                            if np.abs((frac[2] - 1) * 100) <= keep_perc:
                                keep_match = True
                                break
                
                for frac in rm_fracs:
                    if np.abs((frac[0] - 1) * 100) <= rm_perc:
                        if np.abs((frac[1] - 1) * 100) <= rm_perc:
                            if np.abs((frac[2] - 1) * 100) <= rm_perc:
                                rm_match = True
                                break
                
                if keep_match == False or rm_match == True:
                    filtered[y,x] = (255,255,255)

pcv.plot_image(filtered)


# Threshold using the 'a' lab channel to pick out green leaves
channel_a = pcv.rgb2gray_lab(filtered, 'a')
thresh = pcv.threshold.binary(channel_a, 123, 255, 'dark')

# Clean up the noise from the mask by opening and blurring pixels together.
opened = pcv.opening(thresh)
mask2 = pcv.median_blur(opened, 3)

# Apply the new mask to the VIS image
masked = pcv.apply_mask(filtered, mask2, 'white')

#-------------------------------------------------------------------------------------------------------------------#
# It is very important to note that we want to avoid having extract the 'a' lab colour channel, as this is only
# effective if the plant is green. This step is included temporarily, as we search for an alternative that works
# universally, for plants of any colour. One suggestion is to find the average RGB values of the pixels in filtered,
# and remove pixels if their RGB values are not similar to this average. This should work, as by this point MOST of
# what is left should be the plant.
#-------------------------------------------------------------------------------------------------------------------#