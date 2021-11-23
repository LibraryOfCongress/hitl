import cv2
import OcrUtils
import pytesseract
import json
import BoxExtraction
from pytesseract import Output
import re
import numpy as np
from cv_utils import CvUtils

class BusinessBlockFinder:
    image_path = None
    debug = False
    original_image = None
    gray_image = None
    full_line_ocr = None
    ocr = None
    binary = None
    min_height_mult = 2 # Height must at least this more than avg
    max_height_mult = 5 # Height must not be more than this * avg
    max_height = 100 
    max_width = 100

    def __init__(self, image_path, min_height_mult = 2, max_height_mult = 4, max_height = 100, max_width = 100):
        self.min_height_mult = min_height_mult
        self.max_height_mult = max_height_mult
        self.max_height = max_height
        self.max_width = max_width
        self.original_image = cv2.imread(image_path)
        self.pre_process_image()
        self.create_page_ocr()

    def rotateImage(self, cvImage, angle: float):
        newImage = cvImage.copy()
        (h, w) = newImage.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return newImage

    # Deskew image
    def deskew(self, cvImage):
        angle = self.getSkewAngle(cvImage)
        return self.rotateImage(cvImage, -1.0 * angle)

    def getSkewAngle(self, cvImage) -> float:
        # Prep image, copy, convert to gray scale, blur, and threshold
        newImage = cvImage.copy()
        gray = cv2.cvtColor(newImage, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (9, 9), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Apply dilate to merge text into meaningful lines/paragraphs.
        # Use larger kernel on X axis to merge characters into single line, cancelling out any spaces.
        # But use smaller kernel on Y axis to separate between different blocks of text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilate = cv2.dilate(thresh, kernel, iterations=5)

        # Find all contours
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)

        # Find largest contour and surround in min area box
        largestContour = contours[0]
        minAreaRect = cv2.minAreaRect(largestContour)

        # Determine the angle. Convert it to the value that was originally used to obtain skewed image
        angle = minAreaRect[-1]
        if angle < -45:
            angle = 90 + angle
        return -1.0 * angle

    def create_page_ocr(self):
        # Get OCR of original gray image
        custom_config = r'--oem 3 --psm 1'
        self.ocr = pytesseract.image_to_data(self.binary, config = custom_config, output_type=Output.DICT)
        self.full_line_ocr = self.get_ocr_full_lines(self.ocr)
        if self.debug:
            with open("ocr.json", "w") as outfile: 
                json.dump(self.full_line_ocr, outfile)

    def pre_process_image(self):
        self.original_image = self.deskew(self.original_image)
        # Blackout ads to make section identification easier

         # reading the image
        self.gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY) # convert2grayscale
        (thresh, self.binary) = cv2.threshold(self.gray_image, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU) # convert2binary

        self.gray_image = self.blackout_ads(self.gray_image)
        self.binary = self.blackout_ads(self.binary)

        if self.debug:
            cv2.imwrite('binary.png', self.binary)
        return

    def blackout_ads(self, image):
        coords = BoxExtraction.box_extraction(image)
        for coord in coords:
            if(self.is_ad(coord)):
                image[coord["y"]: coord["y"] + coord["h"], coord["x"]: coord["x"] + coord["w"]] = 255 
        
        if self.debug:
            cv2.imwrite('without_ads.png', image)
        return image

    def get_coords_from_tuple(self, tuple):
        return tuple[1], tuple[2], tuple[3], tuple[4]

    def box_in_parent(self, bb_parent, bb_child):
        # Is x1 and y1 in parent
        return bb_parent["x1"] < bb_child["x1"] and bb_parent["x2"] > bb_child["x1"] and bb_parent["y1"] < bb_child["y1"] and bb_parent["y2"] > bb_child["y1"]
    def get_business_listing(self, x, y, width, height):
        #print(" x: " + str(x) + " y:" + str(y) + " width:" + str(width) + " height:" + str(height))
        lines = list()
        listing_bb = self.get_bounding_box(x, y, width, height)
        listing = ''        
        listings = list()
        min_x = None
        min_y = None
        max_x = None
        max_y = None
        for index in range(len(self.ocr['level'])):
            if len(self.ocr["text"][index].strip())==0:
                continue
            ocr_bb = self.get_bounding_box(self.ocr['left'][index], self.ocr['top'][index], self.ocr['width'][index], self.ocr['height'][index])
            overlap = self.get_box_intersection_overlap(listing_bb, ocr_bb)
            if self.box_in_parent(listing_bb, ocr_bb):
                # Get the full line
                block, level, para, line = self.get_ocr_key_values(index)
                t = self.full_line_ocr[block][level][para][line]
                txt = ''

                for text_item in t:
                    txt += ' ' + text_item[0]
                    x, y, w, h = self.get_coords_from_tuple(text_item)

                    if min_x is None or min_x > x:
                        min_x = x
                    
                    if min_y is None or min_y > y:
                        min_y = y

                    if max_x is None or max_x < x + w:
                        max_x = x + w

                    if max_y is None or max_y < y + h:
                        max_y = y + h

                if txt not in lines:
                    lines.append(txt)
                    listing+=txt
                    if self.is_phone(txt):
                        listings.append((listing, min_x, min_y, max_x - min_x, max_y - min_y))
                        listing = ''
                        min_x = None
                        min_y = None
                        max_x = None
                        max_y = None
        
        l = '\r\n'.join([str(elem) for elem in lines]) 

        return l, listings



    def get_business_blocks(self):
        sections = self.get_headlines_and_items()
        for key in sections.keys():
            section = sections[key]
            box = section["box"]
            x1 = box[1]
            y1 = box[2]
            x2 = box[1] + box[3]
            y2 = box[2] + box[4]
            section_x1 = x1
            section_x2 = x2
            section_y1 = y1
            section_y2 = y2
            page_width = self.original_image.shape[1]                
            page_height = self.original_image.shape[0]
            for item in section["items"]:
                item_x1 = item["x"]
                item_y1 = item["y"]
                item_x2 = item_x1 + item["w"]
                item_y2 = item_y1 + item["h"]
                #if item_x1 < section_x1:
                    #section_x1 = item_x1
                
                if item_x2 > section_x2:
                   section_x2 = item_x2

                if item_y2 > section_y2:
                    section_y2 = item_y2
            section["group"] = {
                "x": section_x1,
                "y": section_y1,
                "w": section_x2 - section_x1,
                "h": section_y2 - section_y1
            }
                    

            cv2.rectangle(self.original_image, (section_x1,section_y1), (section_x2,section_y2), (0, 0, 255), 1)        

        cv2.imwrite('sections.png', self.original_image)
        return sections

    def get_headlines_and_items(self):
        candidate_headline_boxes = self.find_headline_candidates()
        text_sections = self.find_text_sections(candidate_headline_boxes)
        return text_sections

    def is_phone(self, text):
        rgxpattern2 = r'\d{4}'
        regexp2 = re.compile(rgxpattern2)
        #if regexp2.search(text) is not None:
         #   return True

        #print ("Checking phone " + text)
        rgxpattern = r'(^\d*\d{1}-\d{4})$'
        regexp = re.compile(rgxpattern)
        if regexp.search(text) is not None:
            return True
        else: 
            rgxpattern2 = r'[A-Za-z]*[\d][\d][\d]'
            regexp2 = re.compile(rgxpattern2)
            if regexp2.search(text) is not None:
                return True
        #print("FOUND PHONE")
        return False

    def get_line_box(self, block_num, level, par_num, line_num):
        x = None
        y = None
        w = None
        h = None
        max_x = None 
        max_y = None
        line_text = ""
        for hlw in self.full_line_ocr[block_num][level][par_num][line_num]:
            if len(hlw[0].strip())==0:
                continue

            line_text += hlw[0] + " "
            
            if x is None or x > hlw[1]:
                x = hlw[1]

            if y is None or y > hlw[2]:
                y = hlw[2]
            
            if max_x is None or max_x < hlw[1] + hlw[3]:
                max_x = hlw[1] + hlw[3]

            if max_y is None or max_y < hlw[2] + hlw[4]:
                max_y = hlw[2] + hlw[4]

        w = max_x - x
        h = max_y - y

        tup = (line_text, x, y, w, h)

        return tup


    def get_x_overlap(self, hl_x1, hl_x2, x1, x2):
        min_x = min(hl_x2, x2)
        max_x = max(hl_x1, x1)

        overlap = min_x - max_x
        return overlap / (x2-x1)
    
    def has_x_overlap(self, hl_x1, hl_x2, x1, x2):
        return x1 > hl_x1 and x1 < hl_x2

    def find_text_sections(self, headline_boxes):
        #overlap_threshold = .01
        text_sections = dict()
        
        # Iterate through full lines that contain phone numbers, find the nearest headline
        # Nearest headline has:
        #   -X overlap > overlap_threshold 
        #   -Is to the right of the headline
        #   -Closest on the Y value to headline
        for i in range(len(self.ocr['line_num'])):
            
            if self.is_phone(self.ocr['text'][i]) == False:
                continue
            
            block, level, para, line = self.get_ocr_key_values(i)
            line_box = self.get_line_box(block, level, para, line)

            if self.debug:
                print(line_box)

            x1  = line_box[1]
            x2  = line_box[1] + line_box[3]
            y1  = line_box[2]
            closest_key = None
            closest_y_dist = None
            for hlb in headline_boxes.keys():
                box = headline_boxes[hlb]
                hl_x1 = float(box[1])
                hl_x2 = float(box[1] + box[3])

                #overlap = self.get_x_overlap(hl_x1, hl_x2, x1, x2)

                if self.debug:
                    print("    **** " + box[0] +  "Overlap: " + str(self.has_x_overlap(hl_x1, hl_x2, x1, x2)) + " Box X: (" + str(hl_x1) + "," + str(hl_x2) + ")")

                # It overlaps, headline is to the left of the text, and it is below the headliner
                #if overlap > overlap_threshold and y1 > box[2] and hl_x1 - 10 < x1:
                if self.has_x_overlap(hl_x1, hl_x2, x1, x2) and y1 > box[2] and hl_x1 - 10 < x1:
                    # It is the closest Y distance
                    if closest_y_dist is None or (y1-box[2]) < closest_y_dist:
                        closest_y_dist = y1-box[2]
                        closest_key = hlb
            if closest_key is not None:
                print("The closest box is "  + headline_boxes[closest_key][0])
                if closest_key not in text_sections.keys():
                    text_sections[closest_key]= {
                        "name": headline_boxes[closest_key][0],
                        "box": headline_boxes[closest_key],
                        "items": list()
                    }
                text_sections[closest_key]["items"].append(
                    {
                        "text": line_box[0],
                        "x": line_box[1],
                        "y": line_box[2],
                        "w": line_box[3],
                        "h": line_box[4],
                    }
                )
        return text_sections

    def find_headline_candidates(self):
        page_width = self.original_image.shape[1]
        mask = self.create_filtered_image()

        # Get OCR of filtered image
        custom_config = r'--oem 3 --psm 11'
        mask_ocr = pytesseract.image_to_data(mask, config = custom_config, output_type=Output.DICT)
        candidates = self.get_headline_candidates(mask_ocr)
        candidate_boxes = self.contruct_headline_boxes(candidates)
        filtered_candidates = self.filter_headliner_boxes(candidate_boxes, page_width)
        if self.debug:
            print(candidates)
            print(filtered_candidates)
        return filtered_candidates


    def get_ocr_coordinate_tuple(self, ocr, index):
        return (ocr['left'][index], ocr['top'][index], ocr['width'][index], ocr['height'][index])

    def get_ocr_key_values(self, index):
        block = self.ocr['block_num'][index]
        line = self.ocr['line_num'][index]
        para = self.ocr['par_num'][index]
        level = self.ocr['level'][index]
        return block, level, para, line

    def get_ocr_key_line(self, index):
        block, level, para, line = self.get_ocr_key_values(index)
        key = str(block) + "-" + str(level) + "-" + str(para) + "-" + str(line)
        return key, self.full_line_ocr[block][level][para][line]

    ## Iterate through all of the lines, define which ones could be headlines
    def get_headline_candidates(self, mask_ocr):
        candidates = {}
        for index in range(len(self.ocr['level'])):
            if len(self.ocr["text"][index].strip())==0:
                continue

            (x, y, w, h) = self.get_ocr_coordinate_tuple(self.ocr, index)
            
            #if h < avgheight * 2 or h > avgheight * 4:
                #continue

            full_bb = self.get_bounding_box(x-10, y-10, w+10, h+10)
            for index1 in range(len(mask_ocr['level'])):
                # Check to make sure this isn't empty.
                if len(mask_ocr["text"][index1].strip())==0:
                    continue

                (x1, y1, w1, h1) = self.get_ocr_coordinate_tuple(mask_ocr, index1)
                
                #if h1 < avgheight * 2 or h1 > avgheight * 4:
                    #continue

                mask_bb = self.get_bounding_box(x1, y1, w1, h1)
                #rint(mask_bb)
                # Find the overlap between the mask and the complete ocr
                #overlap = self.get_box_intersection(full_bb, mask_bb)
                # if overlap == 0:
                #     mask_bb = self.get_bounding_box(x1-20, y1-20, w1 + 20, h1 + 20)
                #     overlap = self.get_box_intersection(mask_bb, full_bb)
                #if overlap > overlap_threshold:

                if self.box_in_parent(full_bb, mask_bb):
                    key, line = self.get_ocr_key_line(index)
                    candidates[key] = line
                    break
        return candidates

    def valid_headline_pattern(self, text):
        rgxpattern = r'(?![A-Za-z\'— ()&]).'
        regexp = re.compile(rgxpattern)
        if regexp.search(text) is not None:
            return False
        return True

    def filter_headliner_boxes(self, headline_boxes, page_width):
        filtered = dict()
        max_page_width_pct = .55
        for box_key in headline_boxes.keys():
            box = headline_boxes[box_key]
            if box[3] > page_width * max_page_width_pct:
                continue
            if box[0] == box[0].upper():
                continue
            if self.is_phone(box[0]) == True:
                continue 
            if self.valid_headline_pattern(box[0]) == False:
                continue 
            filtered[box_key] = box
        return filtered

    def contruct_headline_boxes(self ,headline_candidates):
        headline_boxes = {}
        for hlk in headline_candidates.keys():
            hl_words = headline_candidates[hlk]
            line_text = ""
            x = None
            y = None
            w = None
            h = None
            max_x = None 
            max_y = None
            iter = 0
            # Iterate through the words, find the box that defines the entire headline
            for hlw in hl_words:
                iter+=1
                if len(hlw[0].strip())==0:
                    continue
                line_text += hlw[0] + " "
                if x is None or x > hlw[1]:
                    x = hlw[1]
                if y is None or y > hlw[2]:
                    y = hlw[2]
                
                if max_x is None or max_x < hlw[1] + hlw[3]:
                    max_x = hlw[1] + hlw[3]

                if max_y is None or max_y < hlw[2] + hlw[4]:
                    max_y = hlw[2] + hlw[4]

                if "—" in hlw[0]:
                    w = max_x - x
                    h = max_y - y
                    headline_boxes[hlk + str(iter)] = (line_text, x, y, w, h)
                    line_text = ""
                    x = None
                    y = None
                    w = None
                    h = None
                    max_x = None 
                    max_y = None

            if max_x is not None and max_y is not None:
                w = max_x - x
                h = max_y - y

                headline_boxes[hlk + str(iter)] = (line_text, x, y, w, h)
        return headline_boxes

    def get_bounding_box(self, x, y, w, h):
        return {
            "x1": x,
            "y1": y,
            "x2": x+w,
            "y2": y+h
        }

    def create_filtered_image(self):
        ## Define height heuristics:
        # min_height_mult = 1.5 # Height must at least this more than avg
        # max_height_mult = 4 # Height must not be more than this * avg
        # max_height = 100 
        # max_width = 100
        mask = np.ones(self.original_image.shape[:2], dtype="uint8") * 255 # create blank image of same dimension of the original image

        (contours, _) = cv2.findContours(~self.binary, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE) 

        heights = list()

        for contour in contours:
            [x,y,w,h] = cv2.boundingRect(contour)
            if h < self.max_height and w < self.max_width:
                heights.append(cv2.boundingRect(contour)[3])
        if len(heights) == 0:
            return mask

        avgheight = sum(heights)/len(heights) # average height

        # finding the larger contours
        # Applying Height heuristic
        for c in contours:
            [x,y,w,h] = cv2.boundingRect(c)
            if h > avgheight * self.min_height_mult  and h < avgheight * self.max_height_mult:# and h < max_height and w < max_width:
                cv2.drawContours(mask, [c], -1, 0, -1)

        if self.debug:
            cv2.imwrite('filter.png', mask)
        return mask

    def get_ocr_full_lines(self, text):
        data = {}
        for i in range(len(text['line_num'])):
            txt = text['text'][i]
            block_num = text['block_num'][i]
            line_num = text['line_num'][i]
            par_num = text['par_num'][i]
            level = text['level'][i]
            top, left = text['top'][i], text['left'][i]
            width, height = text['width'][i], text['height'][i]
            if not (txt == '' or txt.isspace()):
                tup = (txt, left, top, width, height)
                if block_num in data:
                    if level in data[block_num]:
                        if par_num in data[block_num][level]:
                            if line_num in data[block_num][level][par_num]:
                                data[block_num][level][par_num][line_num].append(tup)
                            else:
                                data[block_num][level][par_num][line_num] = [tup]
                        else:
                            data[block_num][level][par_num] = {}
                            data[block_num][level][par_num][line_num] = [tup]
                    else:
                        data[block_num][level] = {}
                        data[block_num][level][par_num] = {}
                        data[block_num][level][par_num][line_num] = [tup]
                else:
                    data[block_num] = {}
                    data[block_num][level] = {}
                    data[block_num][level][par_num] = {}
                    data[block_num][level][par_num][line_num] = [tup]
        return data


    def get_box_intersection(self, bb1, bb2):

        assert bb1['x1'] < bb1['x2']
        assert bb1['y1'] < bb1['y2']
        assert bb2['x1'] < bb2['x2']
        assert bb2['y1'] < bb2['y2']

        # determine the coordinates of the intersection rectangle
        x_left = max(bb1['x1'], bb2['x1'])
        y_top = max(bb1['y1'], bb2['y1'])
        x_right = min(bb1['x2'], bb2['x2'])
        y_bottom = min(bb1['y2'], bb2['y2'])

        
        #if x_right < x_left or y_bottom < y_top:
        #    return 0.0

        # The intersection of two axis-aligned bounding boxes is always an
        # axis-aligned bounding box
        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # compute the area of both AABBs
        bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
        bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

        if bb1_area - intersection_area == 0:
            return 1.0
        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = intersection_area / float(bb1_area - intersection_area)
        if iou < 0 or iou > 1:
            return 0
        return iou
    
    def get_box_intersection_overlap(self, bb1, bb2):
        x_left = max(bb1['x1'], bb2['x1'])
        y_top = max(bb1['y1'], bb2['y1'])
        x_right = min(bb1['x2'], bb2['x2'])
        y_bottom = min(bb1['y2'], bb2['y2'])


        # The intersection of two axis-aligned bounding boxes is always an
        # axis-aligned bounding box
        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # compute the area of both AABBs
        bb1_area = (bb1['x2'] - bb1['x1']) * (bb1['y2'] - bb1['y1'])
        bb2_area = (bb2['x2'] - bb2['x1']) * (bb2['y2'] - bb2['y1'])

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        #print("BB1: " + str(bb1))
        #print("BB2: " + str(bb2))
        if (bb1_area + bb2_area) - intersection_area == 0:
            return 0
        iou = intersection_area / float((bb1_area + bb2_area) - intersection_area)
        if iou < 0 or iou > 1:
            return 0
        return iou

    def is_ad(self, coord):
        width_pct = coord["w"]/coord["orig_width"]
        height_pct = coord["h"]/coord["orig_height"]
        if width_pct > .60 or height_pct > .8:
            return False
        elif coord["h"] > 75 and coord["w"] > 75:
            return True
        return False