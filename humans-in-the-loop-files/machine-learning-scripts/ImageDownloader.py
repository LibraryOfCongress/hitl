#
# Download images from the LOC IIIF server and store them locally
#
import requests
from pathlib import Path
import shutil
import time
base = 'https://www.loc.gov/'
iiifbase = 'https://tile.loc.gov/image-services/iiif/'

def getImages(item, dest_dir):
    downloaded_images = list()
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    imagenum = item['start']
    while imagenum <= item['end']:
        imgurl = iiifbase + item['service'].format(str(imagenum).zfill(4))
        r = requests.get(imgurl, stream=True)
        if r.status_code == 200:
            imgname = item['lc_id'] + '_' + str(imagenum).zfill(4) + '.jpg'
        imgpath = dest_dir + '/' + imgname
        image_info = {
            "image_name": imgname,
            "image_location": dest_dir,
            "source": imgurl,
            "image_url": "https://www.loc.gov/resource/{}/?sp={}".format(item['lc_id'], str(imagenum).zfill(4)).replace("gdcustel", "usteledirec")
        }
        downloaded_images.append(image_info)
        with open(imgpath, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
            time.sleep(1)
        imagenum += 1
        print(imgurl)
    return downloaded_images