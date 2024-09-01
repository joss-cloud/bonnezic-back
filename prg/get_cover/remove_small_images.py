from pathlib import Path
import re, os,time
import os.path,glob
from io import BytesIO
from PIL import Image

def get_local_image_dimensions(image_path):
    try:
        # Ouvrir l'image située à image_path
        with Image.open(image_path) as img:
            width, height = img.size
            if (width<300) or (height<300):
                print(f"{image_path} : {width}x{height}")
                os.remove(image_path)
    except IOError as e:
        print(f"Erreur lors de l'ouverture de l'image {image_path} : {e}")
        height=0
img_folder = "/home/web/bonnezic.com/img_music"
# img_folder = "/home/web/bonnezic.com/album"
glob_path = f"{img_folder}/**/*.*"

for img_file in glob.glob(glob_path, recursive=True):
    get_local_image_dimensions(img_file)
    