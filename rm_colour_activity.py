# import the necessary packages
import cv2
import numpy as np

# Path of the VIS image to be read in 
vis_filename = ''

# Define how many colours you want to pick
num_colours = 3



# In this function, define what should happen after mouse click events
def click_and_crop(event, x, y, flags, param):
    
    # grab references to the global variables
    global refPt, cropping, sel_rect_endpoint

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being performed
    if event == cv2.EVENT_LBUTTONDOWN:
        cropping = True
        refPt = [(x, y)]

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest
        cv2.rectangle(image, refPt[0], refPt[1], (0, 0, 255), 2)
        cv2.imshow("image", image)
    
    # Draw the rectangle as the mouse moves
    elif event == cv2.EVENT_MOUSEMOVE:
        if cropping == True:
            sel_rect_endpoint = [(x,y)]





# The selected ROIs will be saved to this list
roi_list = []

for _ in range(num_colours):
    
    # The corners of the rectangle will be saved to this list
    refPt = []
    
    cropping = False
    
    # This list will be used to draw the rectangle as the mouse moves
    sel_rect_endpoint = []
    
    # load the image, clone it, and setup the mouse callback function
    image = cv2.imread(vis_filename, cv2.IMREAD_COLOR)
    clone = image.copy()
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", click_and_crop)
    
    # Keep looping until the 'q' key is pressed.
    # This is where we define what should happen after a keyboard button press.
    while True:
        
    	# display the image and wait for a keypress
        if not cropping:
            cv2.imshow('image', image)
        elif cropping and sel_rect_endpoint:
            rect_cpy = image.copy()
            cv2.rectangle(rect_cpy, refPt[0], sel_rect_endpoint[0], (0,0,255), 1)
            cv2.imshow('image', rect_cpy)
    
        key = cv2.waitKey(1) & 0xFF
        
        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
           image = clone.copy()
    
    	# if the 'c' key is pressed, crop and break from the loop
        elif key == ord("c"):
           break
    
    
    # if there are two reference points (as there should be after you crop),
    # display the region of interest in a separate window.
    if len(refPt) == 2:
    	roi = clone[min(refPt[0][1],refPt[1][1]):max(refPt[0][1], refPt[1][1]),
                    min(refPt[0][0],refPt[1][0]):max(refPt[0][0],refPt[1][0])]
    	cv2.imshow("ROI", roi)
    	cv2.waitKey(0)
    
    # close all open windows
    cv2.destroyAllWindows()
    
    # Save the roi to the list above
    roi_list.append(roi)


# Create an array that you will save your colours to.
colours = np.eye(num_colours, 3)
for i,image in enumerate(roi_list):

    b_array = image[:,:,0]
    g_array = image[:,:,1]
    r_array = image[:,:,2]
    
    b_avg = np.average(b_array)
    g_avg = np.average(g_array)
    r_avg = np.average(r_array)
    
    colours[i, 0] = b_avg
    colours[i, 1] = g_avg
    colours[i, 2] = r_avg
    
# Save your colour array as a csv file so the other scripts can access them.
np.savetxt('rm_colours.csv', colours, delimiter = ',')