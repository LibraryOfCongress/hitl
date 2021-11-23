# Define a set of images, download the images locally, create a json inventory of all images downloaded

import ImageDownloader
import json
from Repository import Repository
from DataSource import DataSource
def main():
    print("Starting image downloader")
    repo = Repository()
    items = [{'location_year':'Birmingham_1955', 'lc_id':'gdcustel.usteledirec00004', 'start':3, 'end':159, 
          'service':'service:gdc:gdcustel:us:te:le:di:re:c0:00:04:usteledirec00004:usteledirec00004_{}/full/pct:100/0/default.jpg'},
         {'location_year':'Dubuque_1943', 'lc_id':'usteledirec.usteledirec05650', 'start':52, 'end':76,
          'service':'service:gdc:gdcustel:us:te:le:di:re:c0:56:50:usteledirec05650:usteledirec05650_{}/full/pct:100/0/default.jpg'},
            {'location_year':'Colorado_Springs_1954', 'lc_id':'gdcustel.usteledirec03932', 'start':67, 'end':181, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:39:32:usteledirec03932:usteledirec03932_{}/full/pct:100/0/default.jpg'},
            {'location_year':'Chicago_Czech_Slovak_1939', 'lc_id':'gdcustel.usteledirec04986x', 'start':55, 'end':70, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:49:86:x:usteledirec04986x:usteledirec04986x_{}/full/pct:100/0/default.jpg'}
            ]

    items2 = [{'location_year':'Philadelphia_1936', 'lc_id':'gdcustel.usteledirec08093', 'start':154, 'end':200, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:80:93:usteledirec08093:usteledirec08093_{}/full/pct:50/0/default.jpg'},
            {'location_year':'Huntington_Beach_1936', 'lc_id':'gdcustel.usteledirec02139', 'start':300, 'end':350, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:21:39:usteledirec02139:usteledirec02139_{}/full/pct:50/0/default.jpg'}
            ]

    items3 = [{'location_year':'Daytona_Beach_1948', 'lc_id':'gdcustel.usteledirec06885', 'start':44, 'end':104, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:68:85:usteledirec06885:usteledirec06885_{}/full/pct:50/0/default.jpg'},
            {'location_year':'Colorado_Springs_1954', 'lc_id':'gdcustel.usteledirec03932', 'start':67, 'end':181, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:39:32:usteledirec03932:usteledirec03932_{}/full/pct:50/0/default.jpg'}
            ]

    items4 = [{'location_year':'Little_Rock_1957', 'lc_id':'gdcustel.usteledirec01216', 'start':123, 'end':273, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:12:16:usteledirec01216:usteledirec01216_{}/full/pct:50/0/default.jpg'},
            {'location_year':'Chicago_Czech_Slovak_1939', 'lc_id':'gdcustel.usteledirec04986x', 'start':55, 'end':70, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:49:86:x:usteledirec04986x:usteledirec04986x_{}/full/pct:50/0/default.jpg'}
            ]
    items5 = [
            {'location_year':'Colorado_Springs_1954', 'lc_id':'gdcustel.usteledirec03932', 'start':67, 'end':181, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:39:32:usteledirec03932:usteledirec03932_{}/full/pct:100/0/default.jpg'},
            {'location_year':'Chicago_Czech_Slovak_1939', 'lc_id':'gdcustel.usteledirec04986x', 'start':55, 'end':70, 
            'service':'service:gdc:gdcustel:us:te:le:di:re:c0:49:86:x:usteledirec04986x:usteledirec04986x_{}/full/pct:100/0/default.jpg'}
            ]
# For each defined set of images
    for item in items:
        # Create a data source
        ds = DataSource()
        ds.name = item['location_year']
        ds.type = 'digital object'
        ds.source_system = 'lc'
        ds.source_id = item['lc_id']
        ds.source_image_url = None
        ds.source_url = item['service']
        data_source_id = repo.insert_data_source(ds)
        # Define a local output directory
        output_dir = "./output/"  + item['location_year']
        images = ImageDownloader.getImages(item, output_dir)
        for image in images:
            print(image)
            image["parent_id"] = data_source_id
            image["source_id"] = item['lc_id']
            
        # Create a json inventory of images
        with open(output_dir + "/image_inventory.json", 'w') as outfile:
            json.dump(images, outfile, default=lambda x: x.__dict__)
            
if __name__ == "__main__":
    main()