import os
import BoxExtraction
from Repository import Repository
from DataSource import DataSource
from Annotation import Annotation
from Coordinate import Coordinate
from datetime import datetime

class Identifier:
    repo = None
    conf = None
    def __init__(self):
        self.repo = Repository()
        self.conf = self.repo.config(filename='database.ini', section='ml')

    def create_output_directory(self, data_source, type):
        image_base_name = os.path.basename(data_source.location)
        source_image_dir = data_source.location.replace(image_base_name,'')
        output_dir = os.path.join(source_image_dir, 'cropped', type)
        self.ensure_dir(output_dir)
        return output_dir

    def create_annotation(self, data_source, output_dir, cropped_image_name, coord, ml_process_name, image_path, subject_type):
        cropped_image_path = os.path.join(output_dir, cropped_image_name)
        BoxExtraction.create_cropped_image(image_path, cropped_image_path, coord["x"], coord["y"], coord["w"], coord["h"])
        
        process_id = self.repo.get_ml_process_id(ml_process_name)
        version_number = self.conf["version"]
        ml_version_id = self.repo.get_ml_version_id(process_id, version_number)

        if ml_version_id == 0:
            ml_version_id = self.repo.insert_ml_version(process_id, version_number)

        # Create a data source
        ann = Annotation()
        source_type = None
        if subject_type == 'page':
            source_type = 'digital object image'
        elif subject_type == 'ad':
            source_type = 'page'

        ann.source_type = source_type
        ann.ml_version_id = ml_version_id
        ann.data_source_id = data_source.id
        ann.created_at = datetime.now()
        ann.subject_type = subject_type
        ann.local_path = cropped_image_path
        ann.id = self.repo.insert_annotation(ann)
        
        c = Coordinate()
        c.x = coord["x"]
        c.y = coord["y"]
        c.width = coord["w"]
        c.height = coord["h"]
        c.annotation_id = ann.id
        self.repo.insert_coordinates(c)
        ann.coordinates.append(c)

        return ann

    def identify_border(self, coords):
        for coord in coords:
            width_pct = coord["w"]/coord["orig_width"]
            height_pct = coord["h"]/coord["orig_height"]
            if width_pct > .75 and height_pct > .75:
                return coord
        return None

    def identify_pages(self, data_sources):
        annotations = list()

        idx = 0
        for data_source in data_sources:
            # Iterate through, process image, identify pages
            output_dir = self.create_output_directory(data_source, "page")

            coords = BoxExtraction.box_extraction(data_source.location, output_dir)
            #border = self.identify_border(coords)

            input_location = data_source.location
            file_name = BoxExtraction.get_file_name(data_source.location)
            print(file_name)
            # x_adjusted = 0
            # y_adjusted = 0
            # width_adjusted = 0
            # height_adjusted = 0
            # if border is not None:
            #     data_source.location = output_dir + file_name + "_nb.png"
            #     print("FOUND BORDER")

            #     BoxExtraction.create_cropped_image(input_location, data_source.location, border["x"], border["y"], border["w"], border["h"])

            coords =  BoxExtraction.box_extraction(data_source.location, output_dir)

            page_count = 0
            for coord in coords:
                idx += 1
                cropped_image_name = file_name + "_" + str(idx) + '.png'
                if self.is_page(coord):
                    page_count +=1
                else:
                    continue
                ml_process_name = 'OpenCV -- page'
                ann = self.create_annotation(data_source, output_dir, cropped_image_name, coord, ml_process_name, data_source.location, 'page')
            
            if page_count==0 and len(coords)>0:
                ml_process_name = 'OpenCV -- page'
                idx += 1
                cropped_image_name = file_name + "_" + str(idx) + '.png'
                coord1 = coords[0]

                ca = dict()
                ca["x"] = 0
                ca["y"] = 0
                ca["w"] = int(coord1["orig_width"]/2)
                ca["h"] = coord1["orig_height"]
                print("creating " + cropped_image_name)
                print(ca)
                ann = self.create_annotation(data_source, output_dir, cropped_image_name, ca, ml_process_name, data_source.location, 'page')
            

                idx += 1
                cropped_image_name = file_name + "_" + str(idx) + '.png'
                print("creating " + cropped_image_name)
                cb = dict()
                cb["x"] = int(coord1["orig_width"]/2)
                cb["y"] = 0
                cb["w"] = int(coord1["orig_width"]/2)
                cb["h"] = coord1["orig_height"]
                ann = self.create_annotation(data_source, output_dir, cropped_image_name, cb, ml_process_name, data_source.location, 'page')
            

        return annotations

    def insert_page_data_source(self, image_name, image_location, parent_id, annotation_id, suffix, source_id, height, width, x, y):
        print(suffix)
        repo = Repository()
        ds = DataSource()
        ds.name = image_name.replace(".jpg", '') + suffix
        ds.type = 'page'
        ds.source_system = 'ml'
        ds.source_id = source_id
        ds.location = image_location
        ds.parent_id = parent_id
        ds.height = height
        ds.width = width
        ds.x = x
        ds.y = y
        ds.annotation_id = annotation_id
        ds.id = repo.insert_data_source(ds)
        return ds

    def identify_ads(self):
        repo = Repository()
        conf = repo.config(filename='database.ini', section='ml')
        idx = 0
        # Get a list of pages
        annotations = repo.get_page_annotations()
        page_count = 0
        print("Annotation Length: " + str(len(annotations)))
        # for each page
        for annotation in annotations:
            page_data_source = None
            data_source = repo.get_data_source(annotation.data_source_id)
            annotation.coordinates = repo.get_coordinates(annotation.id)
            c = annotation.coordinates[0]
            page_location = "./output/pages/page_" + str(page_count) +".png"
            BoxExtraction.create_cropped_image(data_source.location, page_location, c.x, c.y, c.width, c.height)
            # Iterate through, process image, identify pages
            output_dir = self.create_output_directory(data_source, "ads")
            coords = BoxExtraction.box_extraction(page_location, output_dir)
            file_name = BoxExtraction.get_file_name(data_source.location)
            
            if page_data_source is None:
                suff = self.get_page_name_suffix(c.x, data_source.width)
                page_data_source = self.insert_page_data_source(data_source.name, page_location, data_source.id, annotation.id, suff, data_source.source_id, c.height, c.width, c.x, c.y)
                
            for coord in coords:
                idx += 1
                cropped_image_name = file_name + "_" + str(idx) + '.png'
                if self.is_ad(coord):
                    page_count +=1
                else:
                    continue
                ml_process_name = 'OpenCV -- ads'
                ann = self.create_annotation(page_data_source, output_dir, cropped_image_name, coord, ml_process_name, page_location, 'ad')
                
            # for annotation in annotations:
            #     if len(annotation.coordinates) > 0:
            #         CvUtils.blackout_ads(page_location, annotation.coordinates)
    
    def get_page_name_suffix(self, x, width):
        if x < width*.40:
            return "_a"
        return "_b"

    def is_page(self, coord):
        width_pct = coord["w"]/coord["orig_width"]
        height_pct = coord["h"]/coord["orig_height"]
        if width_pct > .35 and width_pct < .55 and height_pct > .8:
            return True
        return False

    def is_ad(self, coord):
        print(coord)
        width_pct = coord["w"]/coord["orig_width"]
        height_pct = coord["h"]/coord["orig_height"]
        if width_pct > .35 and width_pct < .55 and height_pct > .8:
            return False
        elif width_pct > .35 or height_pct > .8:
            return False
        elif coord["h"] > 75 and coord["w"] > 75:
            return True
        return False
        
    def ensure_dir(self, file_path):
        directory = os.path.abspath(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory