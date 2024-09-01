from pathlib import Path
from PIL import Image
import os, glob

def get_local_image_dimensions(image_path):
    try:
        # Open the image located at image_path
        with Image.open(image_path) as img:
            width, height = img.size
            # Check if the image is not square and significantly different in dimensions
            print(f"{image_path} : {width}x{height}")
            if width != height and (width > height * 1.05 or height > width * 1.05):
                crop_image_to_square(image_path)
    except IOError as e:
        print(f"Error opening image {image_path}: {e}")

def image_resize(image_path_to_be_resized):
    img_name = Path(image_path_to_be_resized).stem
    img_file_squared = img_square_folder + img_name + ".jpg"
    try:
        with Image.open(image_path_to_be_resized) as img:
            width, height = img.size
            # Resize the image if its width is greater than 600
            if width > 600:
                print(f"image_resize to {img_file_squared} 600x600")
                img_resized = img.resize((600, 600), Image.LANCZOS)
                img_resized.save(img_file_squared, format='JPEG', quality=95, subsampling=2)

    except IOError as e:
        print(f"Error resizing image {image_path_to_be_resized}: {e}")

def crop_image_to_square(image_to_be_cropped):
    print(f"crop_image_to_square : {image_to_be_cropped}")
    img_name = Path(image_to_be_cropped).stem
    img_file_squared = img_square_folder + img_name + ".jpg"
    try:
        with Image.open(image_to_be_cropped) as img:
            width, height = img.size
            print(f"crop_image_to_square {image_to_be_cropped} : {width}x{height} to {img_file_squared}")
            if width > height:
                # Crop width so the final width = height
                px_to_crop = (width - height) / 2
                left = px_to_crop
                right = width - px_to_crop
                top = 0
                bottom = height
            elif width < height:
                # Crop height so the final height = width
                px_to_crop = (height - width) / 2
                left = 0
                right = width
                top = px_to_crop
                bottom = height - px_to_crop
            print(f"crop image to {img_file_squared} : {left}, {top}, {right}, {bottom}")
            im1 = img.crop((left, top, right, bottom))
            # Corrected save method with subsampling set to '2' (4:2:0)
            im1.save(img_file_squared, format='JPEG', quality=95, subsampling=2)


    except IOError as e:
        print(f"Error cropping image {image_to_be_cropped} : {e}")

# Setting up directories
img_square_folder = "/home/web/bonnezic.com/images_square/"
glob_path = f"{img_square_folder}/**/*.*"

for img_file in glob.glob(glob_path, recursive=True):
    get_local_image_dimensions(img_file)
    image_resize(img_file)
