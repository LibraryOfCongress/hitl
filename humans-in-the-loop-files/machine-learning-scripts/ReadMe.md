# Machine Learning Pipeline
Instructions for initializing the workflow database and running scripts in the machine learning pipeline.  

## Quick Start
- Download and install [postgresql](https://www.postgresql.org/download/)
- Create the database schema
    `./psql -f /yellow-pages.sql -h <ip or host> -d yellow-pages -p 5432 -U postgres`
- Open and modify the following values in database.ini  
    host=**<your database ip address or host name>**  
    user=**<psql username>**
    password=**<pql pw>**
- Download and install [python3](https://www.python.org/downloads/) 
- Install python dependencies
    `pip install -r requirements.txt`
- Run each of the steps in order
-- `python3 ML1.py`
-- `python3 ML2.py`
-- `python3 ML3_4.py`
-- `python3 ML5.py`

## ML 1 - ML.py, ImageDownloader.py
- Iterate through a dictionary of collections to download.  
- Creates new Data_Source records for digital objects 
- Store results in image_inventory.json

## ML 2 - ML2.py, Identifier.py
- For each digital object image data source in ML 1
	- Extract a list of boxes for the image
		- Remove noise from image using OpenCV using medianBlur
		- Create binary image, invert the image
		- Use OpenCV findContours to boxes (only keep boxes with a width to height ratio between .25 and 2.25...somewhat arbitrarily)
	- Identify pages:
		- Identify pages (Width between .35 and .55 of the image.  Height > .8 of image
		- If we don't get 2 pages, split image in half. 
		- Insert data source, annotation, coordinates.  Page data sources have a suffix of _a for the left-most page, and _b for the right-most page
	- Save cropped page image locally
- For each page annotation:
	- Identify ads:
		- Extract boxes 
		- If the boxes match page coordinates, return false
		- If box width is > .35 or height > .8 of the page, return false
		- Otherwise, identify add as box greater than 75 pixels width and height(rough estimate)
	- Insert annotation and coordinates
	
## ML 3 - ML_3_4.py, BusinessBlockFinder.py
- Get list of page data sources
- Pre-process image:
	- De-skew image using OpenCV to help ocr page segmentation alignment
	- Create grayscale image, black out ads identified in ML2
	- Create binary image, black out ads identified in ML2
- Create Page OCR using pyTesseract
	- Page segmentation model 1: Automatic page segmentation with orientation and script detection
- Insert ocr annotation, coordinates, text values
	- Annotation confidence calculated as the median confidence among all words
- Store OCR json locally (data_source.location.ocr.json)
	
​
## ML 4 - ML5.py
- Create OCR data source
- Get a list of business blocks
	- Identify business block listing type
		- Identify a list of candidates
			- Create a filtered image
				- Identify contours using OpenCV 
				- Calculate avg height using max_height and max_width (parameters) as filters to weed out ads and noise
				- Draw contours that are larger than average (>avgheight * multiplier parameter)
			- Run ocr on filtered image with page segmentation 11: Sparse text
			- Identify candidates based on original ocr lines overlapping with filtered text ocr
				- Overlap is defined as the upper left coordinate falls somewhere in the line of text coordinates
			- Filter headline candidates
				- Must be less than .55 of page
				- Is not as wide as width parameter passed in
				- Must not be all caps
				- Must not contain a phone number
				- Must contain [A-z , - ' () &] characters only
	- Identify business listings
		- Iterate through OCR
			- Identify if the line of text contains a phone number (rough estimate of a phone number)
			- Find the closest headline candidate
				- X coordinate of the text overlaps with the headline
        		- X coordinate of the text is to the right of the headline
        		- Identify the closes Y value to text
        - For each section with coordinates identified, create a listing by iterating through OCR for a section until a phone number is found.
    - Keep only headline candidates that have a listing
    - For each business block, insert annotation, coordinates, and full ocr text for the listing
    - For each business block, insert annotation, coordinates, and ocr text for business listing and business type
    
​
## ML 5
- Train spacey_crfsuite using training markdown generated from crowdsourced data and en_core_web_sm
- For all page ocr annotations
	- For all coordinates for this annotation, get the text value.
		- Replace -- with ""
		- Tokenize text value using spacy_crfsuite tokenizer
		- Insert structured data
			- Business group annotation, coordinate, text value
			- Business listing annotation with a text value and coordinates record per entity extracted
				- Listing confidence defined as median confidence based on aggregated CRF results