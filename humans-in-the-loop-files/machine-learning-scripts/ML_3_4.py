# Run OCR on images and identify business blocks using a combination of tesseract, opencv
from numpy.core import multiarray
from BusinessBlockFinder import BusinessBlockFinder
from Repository import Repository
from Annotation import Annotation
from Coordinate import Coordinate
from DataSource import DataSource
from TextValue import TextValue
import json
from os import path
from datetime import datetime

def ml_3_insert_ocr_data(ocr_json, ds):
    version = "1.1.0"
    repo = Repository()
    ml_process_id = repo.get_ml_process_id('Tesseract page OCR')
    ml_version_id = repo.get_ml_version_id(ml_process_id, version)
    if ml_version_id == 0:
        ml_version_id = repo.insert_ml_version(ml_process_id, version)
    local_path = "ocr.json"
    
    avg_confidence = calculate_avg_confidence(ocr_json)

    annotation = Annotation()
    annotation.source_type = 'page'
    annotation.ml_version_id = ml_version_id
    annotation.data_source_id = ds.id
    annotation.confidence = avg_confidence
    annotation.subject_type  = "page ocr"
    annotation.created_at = datetime.now()
    annotation.local_path = ds.location + ".ocr.json"
    annotation.id = repo.insert_annotation(annotation)

    coord = Coordinate()
    coord.x = ds.x
    coord.y = ds.y
    coord.width = ds.width
    coord.height = ds.height
    coord.annotation_id =  annotation.id

    repo.insert_coordinates(coord)

    with open(annotation.local_path, "w") as outfile: 
        json.dump(ocr_json, outfile)

    return annotation

def ml_4_business_blocks(page_ds, page_annotation, bb_finder):
    version = "1.1.0"
    repo = Repository()
    ml_process_id = repo.get_ml_process_id('OCR parsing')
    ml_version_id = repo.get_ml_version_id(ml_process_id, version)
    if ml_version_id == 0:
        ml_version_id = repo.insert_ml_version(ml_process_id, version)
    # Create new data source
    data_source = DataSource()
    data_source.name = page_annotation.local_path
    data_source.type = 'page OCR'
    data_source.source_system = 'ml' 
    data_source.location = None
    data_source.height = page_ds.height
    data_source.width = page_ds.width
    data_source.x = page_ds.x
    data_source.y = page_ds.y
    data_source.parent_id = page_ds.id
    data_source.annotation_id = page_annotation.id
    data_source.id = repo.insert_data_source(data_source)

    business_blocks = bb_finder.get_business_blocks()

    #Output business grouping
    for key in business_blocks:
        this_block = business_blocks[key]
        this_type = this_block["box"]
        this_group = this_block["group"]

        listing_text, listings = bb_finder.get_business_listing(this_group["x"], this_group["y"] + this_type[4], this_group["w"], this_group["h"] - this_type[4])
        
        # annotation = Annotation()
        # annotation.source_type = 'page ocr'
        # annotation.ml_version_id = ml_version_id
        # annotation.data_source_id = data_source.id
        # annotation.created_at = datetime.now()
        # annotation.subject_type = "business grouping"
        # annotation.id = repo.insert_annotation(annotation)

        annotation = insert_annotation('page ocr', ml_version_id, data_source.id, "business grouping", None)
        annotation_coord = insert_coordinate(this_group["x"], this_group["y"], this_group["w"], this_group["h"] , annotation.id)
        business_grouping_text_value = insert_text_value('business grouping', listing_text, annotation_coord.id)
        
        type_annotation = Annotation()
        type_annotation.source_type = 'page ocr'
        type_annotation.ml_version_id = ml_version_id
        type_annotation.data_source_id = data_source.id
        type_annotation.created_at = datetime.now()
        type_annotation.subject_type = "business type"
        type_annotation.parent_id = annotation.id
        type_annotation.id = repo.insert_annotation(type_annotation)

        type_coord = insert_coordinate(this_type[1], this_type[2], this_type[3], this_type[4], type_annotation.id)
        type_value = insert_text_value('business_type_text', this_type[0], type_coord.id)

        for listing in listings:
            listing_annotation = insert_annotation('page ocr', ml_version_id, data_source.id, "business listing", annotation.id)
            listing_coord = insert_coordinate(listing[1], listing[2], listing[3], listing[4], listing_annotation.id)
            listing_value = insert_text_value('business listing', listing[0], listing_coord.id)


            
def insert_annotation(source_type, ml_version_id, data_source_id, subject_type, parent_id):
    repo = Repository()
    annotation = Annotation()
    annotation.source_type = source_type
    annotation.ml_version_id = ml_version_id
    annotation.data_source_id = data_source_id
    annotation.created_at = datetime.now()
    annotation.subject_type = subject_type
    annotation.parent_id = parent_id
    annotation.id = repo.insert_annotation(annotation)
    return annotation

def insert_text_value(key, value, coordinates_id):
    repo = Repository()
    text_value = TextValue()
    text_value.key = key
    text_value.value = value
    text_value.coordinates_id = coordinates_id
    text_value.id = repo.insert_text_value(text_value)
    return text_value

def insert_coordinate(x, y, width, height, annotation_id):
    repo = Repository()
    coord = Coordinate()
    coord.x = x
    coord.y = y
    coord.width = width
    coord.height = height
    coord.annotation_id =  annotation_id
    coord.id = repo.insert_coordinates(coord)
    return coord

        






def main():
           
    repo = Repository()
    data_sources = repo.get_data_source_pages()

    for ds in data_sources:
        print("ds" + str(ds.id))
        exists = path.exists(ds.location)
        mult_min, mult_max, max_hl_height, max_hl_width = get_params(ds.source_id)
        bb = BusinessBlockFinder(ds.location, mult_min, mult_max, max_hl_height, max_hl_width)
        annotation = ml_3_insert_ocr_data(bb.ocr, ds)
        ml_4_business_blocks(ds, annotation, bb)
        
def get_params(source_id):
    mult_min = 2
    mult_max = 5
    max_hl_height = 100
    max_hl_width = 300

    if 'gdcustel.usteledirec00004' in source_id:
        return 2.4, 4, 150, 300
    
    if 'gdcustel.usteledirec03932' in source_id:
        return 2, 5, 150, 300

    if 'gdcustel.usteledirec04986' in source_id:
        return 2, 5, 100, 300

    return mult_min, mult_max, max_hl_height, max_hl_width 
    
def calculate_avg_confidence(ocr_json):
    sum = 0
    for i in range(len(ocr_json["conf"])):
        sum += float(ocr_json["conf"][i])
    return sum/len(ocr_json["conf"])

if __name__ == "__main__":
    main()