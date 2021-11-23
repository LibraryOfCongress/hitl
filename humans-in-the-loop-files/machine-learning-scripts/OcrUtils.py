# OCR Utility functions 
import cv2 
from cv_utils import CvUtils
from pytesseract import Output
from math import sqrt
import numpy as np

def get_lines(img):
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray,50,150,apertureSize = 3)
  minLineLength = 100
  maxLineGap = 10
  lines = cv2.HoughLinesP(edges,1,np.pi/180,100,minLineLength,maxLineGap)
  print(lines[0])
  for line in lines:
    for x1,y1,x2,y2 in line:
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

  cv2.imwrite('houghlines5.png',img)

def is_section_header(line):
  return line["size_group"] >=6 and line["line_num"] == 1 and hasNumbers(line["line"] )==False

def write_image(img, filename):
    cv2.imwrite(filename, img) 

def write_results(results, output_file):
    with open(output_file, "w") as f:
        f.write(results)

def hasNumbers(inputString):
  return any(char.isdigit() for char in inputString)
