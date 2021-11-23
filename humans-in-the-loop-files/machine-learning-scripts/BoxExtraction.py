# Extract boxes from an images.
import cv2
import numpy as np
import os
from cv_utils import CvUtils

# Get the height and width of an image
def get_img_height_width(path):
    img = cv2.imread(path, 0)  # Read the image
    return img.shape

def box_extraction_from_path(img_for_box_extraction_path):
    img = cv2.imread(img_for_box_extraction_path, 0)  # Read the image
    return box_extraction(img)

def box_extraction(img):
    try:
        img = CvUtils.remove_noise(img)
    except:
        print("Error")

    orig_height, orig_width = img.shape

    (thresh, img_bin) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # Thresholding the image
    
    img_bin = 255-img_bin  # Invert the image
    
    # Defining a kernel length
    kernel_length = np.array(img).shape[1]//40
    
    # A verticle kernel of (1 X kernel_length), which will detect all the verticle lines from the image.
    verticle_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_length))
    # A horizontal kernel of (kernel_length X 1), which will help to detect all the horizontal line from the image.
    hori_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_length, 1))
    # A kernel of (3 X 3) ones.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    # Morphological operation to detect verticle lines from an image
    img_temp1 = cv2.erode(img_bin, verticle_kernel, iterations=3)
    verticle_lines_img = cv2.dilate(img_temp1, verticle_kernel, iterations=3)
    # Morphological operation to detect horizontal lines from an image
    img_temp2 = cv2.erode(img_bin, hori_kernel, iterations=3)
    horizontal_lines_img = cv2.dilate(img_temp2, hori_kernel, iterations=3)
    # Weighting parameters, this will decide the quantity of an image to be added to make a new image.
    alpha = 0.5
    beta = 1.0 - alpha
    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(verticle_lines_img, alpha, horizontal_lines_img, beta, 0.0)
    img_final_bin = cv2.erode(~img_final_bin, kernel, iterations=2)
    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # For Debugging
    # Enable this line to see verticle and horizontal lines in the image which is used to find boxes
    cv2.imwrite("img_final_bin.jpg",img_final_bin)
    # Find contours for image, which will detect all the boxes
    contours, hierarchy = cv2.findContours(img_final_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort all the contours by top to bottom.
    (contours, boundingBoxes) = sort_contours(contours, method="top-to-bottom")
    
    idx = 0
    coords = list()
    for c in contours:
        # Returns the location and width,height for every contour
        x, y, w, h = cv2.boundingRect(c)
        
        if (.25 < w/h <2.25 ):# and w > 3*h:
            idx += 1
            coords.append({
                "orig_height": orig_height,
                "orig_width": orig_width,
                "x":x,
                "y":y,
                "w":w,
                "h":h
            })
    
    return coords

def create_cropped_image(original_image, cropped_image_path, x, y, w, h):
    x = int(x)
    y = int(y)
    w = int(w)
    h = int(h)
    img = cv2.imread(original_image, 0)  # Read the image
    new_img = img[y:y+h, x:x+w]
    cv2.imwrite(cropped_image_path, new_img)

def get_file_name(full_path):
    base=os.path.basename(full_path)
    return os.path.splitext(base)[0]

def sort_contours(cnts, method="left-to-right"):
	# initialize the reverse flag and sort index
	reverse = False
	i = 0
	# handle if we need to sort in reverse
	if method == "right-to-left" or method == "bottom-to-top":
		reverse = True
	# handle if we are sorting against the y-coordinate rather than
	# the x-coordinate of the bounding box
	if method == "top-to-bottom" or method == "bottom-to-top":
		i = 1
	# construct the list of bounding boxes and sort them from top to
	# bottom
	boundingBoxes = [cv2.boundingRect(c) for c in cnts]
	(cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
		key=lambda b:b[1][i], reverse=reverse))
	# return the list of sorted contours and bounding boxes
	return (cnts, boundingBoxes)
