import cv2
import random
import numpy as np

# Filenames of the images to be read in
vis_filename = ''
ir_filename = ''

# Initialize the lists of matching points we wish to record on the vis and ir images.
vis_points = []
ir_points = []

# Initialize a list of colours which will correspond to each pair of points.
# It is important that we have a list to record which colours have been used,
# so that the "undo" buton knows which colour to revert to.
colour_list = []

# We will use this variable continously to check whether the last selected
# pixel was in the NIR, or the VIS half of the image.
count = 0


# Define our mouse callback function
def select_pixels(event, x, y, flags, param):
    
    global vis_points, ir_points, count, image_history, colour_list, concat
    
    # If the left mouse button is clicked, add the coordinate of the clicked
    # pixel to either the ir_points list, or vis_points list, depending on
    # which half of the image was clicked on.
    # The user must click the NIR image first, then the VIS image, then NIR
    # again, and so on...
    if event == cv2.EVENT_LBUTTONDOWN:
        count += 1
        
        if 0 <= x <= 720:
            if count % 2 == 1:
                ir_points.append((x,y))
                colour_list.append((random.randint(0,255), 
                                    random.randint(0,255),
                                    random.randint(0,255)))
                cv2.circle(concat, (x,y), 5, colour_list[-1], 2)
                image_history[count] = concat.copy()
            elif count >= 1:
                count -= 1
                
        else:
            if count % 2 == 0:
                vis_points.append((x-720,y))
                cv2.circle(concat, (x,y), 5, colour_list[-1], 2)
                image_history[count] = concat.copy()
            elif count >= 1:
                count -= 1
                
    # If the right mouse button is pressed, delete the most recently clicked
    # pixel from the corresponding points list.
    if event == cv2.EVENT_RBUTTONDOWN:
        if count % 2 == 1:
            ir_points = ir_points[:-1]
            if count >= 1:
                del image_history[count]
                count -= 1
            concat = image_history[count].copy()
            colour_list = colour_list[:-1]
        else:
            vis_points = vis_points[:-1]
            if count >= 1:
                del image_history[count]
                count -= 1
            concat = image_history[count].copy()



# load the images, and concatenate them so we can operate on both the images
# in one window.
vis = cv2.imread(vis_filename, cv2.IMREAD_COLOR)
ir = cv2.imread(ir_filename, cv2.IMREAD_COLOR)
concat = cv2.hconcat([ir, vis])

# Set up a history of all the changes that have been made to the image
# during the mouse callback phase. This is necessary in order to have an
# 'undo' button.
image_history = {}
image_history[count] = concat.copy()

# history_base is necessary to have a 'reset' button, rather than just an
# 'undo' button.
history_base = image_history.copy()

cv2.namedWindow('image')
cv2.setMouseCallback('image', select_pixels)

# keep looping until the 'q' key is pressed
while True:
    
    # display the image and wait for a keypress
    cv2.imshow('image', concat)
    key = cv2.waitKey(1) & 0xFF
    
    # if the 'r' key is pressed, reset both points lists
    if key == ord('r'):
        vis_points = []
        ir_points = []
        image_history = history_base.copy()
        concat = image_history[0].copy()
        count = 0

    # if the 'b' key is pressed, delete the last selected point
    if key == ord('b'):
        if count % 2 == 1:
            ir_points = ir_points[:-1]
            if count >= 1:
                del image_history[count]
                count -= 1
            concat = image_history[count].copy()
            colour_list = colour_list[:-1]
        else:
            vis_points = vis_points[:-1]
            if count >= 1:
                del image_history[count]
                count -= 1
            concat = image_history[count].copy()
    
    # if the 'q' key is pressed, break form the loop (i.e. close window) and
    # save the points that have been selected.
    if key == ord('q'):
        break


# close all open windows
cv2.destroyAllWindows()


# Create an array from our VIS points
src_points = np.array(vis_points)

# Create an array from our NIR points
dst_points = np.array(ir_points)

# Calculate Homography
h, status = cv2.findHomography(src_points, dst_points)


# Save the homography matrix, so we can use it on all of our images.
np.savetxt('h_matrix.csv', h, delimiter = ',')

#aligned = cv2.warpPerspective(vis, h, (vis.shape[1], vis.shape[0]))