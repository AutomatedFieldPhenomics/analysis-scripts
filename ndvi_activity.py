from plantcv import plantcv as pcv
import numpy as np
import pandas as pd
import cv2

class options:
    def __init__(self):
        self.debug = "plot"
        self.writeimg= False


args = options()
 
pcv.params.debug = args.debug

# Read in the image
nir_filename = ''
img, path, filename = pcv.readimage(nir_filename)

    
#----------------------------------------------------------------------------------------------------------------#
# This function takes an NIR image as input and returns two NDVI representations of it. One is a grayscale
# representation of the NDVI values, normalized from 0-255. The other returned image is the result of a specific
# LUT being applied to the grayscale. Ideally, objects coloured violet are possible plant material, while green,
# yellow, orange, and red objects represent plant material.
#---------------------------------------------------------------------------------------------------------------#
def NDVI_lin(image):
    
    # Set up the colour mapped, and grayscale NDVI images
    NDVI_img = np.zeros(shape=[image.shape[0], image.shape[1], 3], dtype=np.uint8)
    grayscale = np.zeros(shape=[image.shape[0], image.shape[1]], dtype=np.uint8)
    
    # Iterate over every pixel in the provided image.
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            
            # Find the B, G, and R values of the pixel.
            pixel = image[y, x]
            B = int(pixel[0])
            G = int(pixel[1])
            R = int(pixel[2])
            
            # Our NDVI formula breaks if both R and B are 0.
            if R == 0 and B == 0:
                R = 1
                B = 1
            
            # Find the NDVI value between -1 and 1 for this pixel.
            ndvi_val = (B-R)/(B+R)
            # Map the NDVI value LINEARLY to the interval [0,255]
            gray_val = int(127.5*(ndvi_val+1))
            # Save this intensity value at the current location (i.e. x and y) on our grayscale image.
            grayscale[y, x] = gray_val
            
    # Normalize the grayscale image for more contrast between plant and non-plant material.
    grayscale = cv2.normalize(grayscale, grayscale, 0, 255, cv2.NORM_MINMAX)

    # Get the new normalized grayscale values for each pixel so we can map them to a colour using the LUT.
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            intensity = grayscale[y, x]
        
            B = lut_dict[intensity][0]
            G = lut_dict[intensity][1]
            R = lut_dict[intensity][2]
            
            NDVI_img[y, x] = [B, G, R]
            
    return NDVI_img, grayscale


def create_mask(grayscale):
           
    ndvi_mask = np.zeros(shape=[img.shape[0], img.shape[1]], dtype=np.uint8)
    
    
    for x in range(img.shape[1]):
        for y in range(img.shape[0]):
            
            # We keep pixels if they are within a certain range in terms of 
            # grayscale intensity
            if X <= gray[y,x] <= 255:
                ndvi_mask[y, x] = gray[y,x]
    
    pcv.plot_image(ndvi_mask)
    
    # We use an opening function which removes noise from the image.
    opened = pcv.opening(ndvi_mask)
    # We blur pixels together, which removes more noise, and cleans up our mask.
    clean = pcv.median_blur(opened, X)
    
    return clean

# Read in the LUT csv file and create a dictionary which we will use to map intensity values to colours.
lut_csv = pd.read_csv('VGYR_lut.csv')
r_series = lut_csv.Red
g_series = lut_csv.Green
b_series = lut_csv.Blue
lut_dict = {}
for num in range(256):
    lut_dict[num] = (b_series[num], g_series[num], r_series[num])
    
# Create the grayscale and coloured NDVI images using the image which was read in above.
ndvi, gray = NDVI_lin(img)
pcv.plot_image(gray)
pcv.plot_image(ndvi)

# Create a mask from the grayscale NDVI image.
mask = create_mask(gray)

# We do not want any definition in the plant, we just want a binary mask where every pixel is either
# black or white.
ndvi_mask = pcv.threshold.binary(mask, 1, 255, 'light')

pcv.print_image(ndvi_mask, 'ndvi_mask.png')