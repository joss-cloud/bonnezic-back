import os
import time
import requests
from PIL import Image, UnidentifiedImageError
import logging


class ResizeDownloadImg:
    def __init__(self):
        pass

    def download_image(self, image_url, save_directory, save_name):
        logging.info(
            "download_image url save_directory: %s %s", image_url, save_directory
        )
        save_path = os.path.join(save_directory, save_name)

        # Check if the image already exists
        if os.path.exists(save_path):
            logging.info("Image already exists at: %s, download skipped.", save_path)
            return save_path

        logging.info("Image %s does not exist", save_path)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

        time.sleep(3)

        try:
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP 4xx/5xx status codes
        except requests.exceptions.RequestException as e:
            logging.error("Error downloading the image from %s : %s", image_url, e)
            return None

        try:
            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            with open(save_path, "wb") as image_file:
                image_file.write(response.content)
                logging.info("Image downloaded and saved at: %s", save_path)

            # Verifying and resizing the image after saving
            self.verify_and_resize_image(save_path)
            return save_path

        except OSError as e:
            logging.error("Error writing the image to disk: %s", e)
            return None

    def verify_and_resize_image(self, image_path):
        """Check and resize the image if necessary."""
        logging.info("verify_and_resize_image image_path : %s", image_path)

        try:
            with Image.open(image_path) as img:
                width, height = img.size
                logging.info("Image dimensions: %sx%s", width, height)

                if width < 400 or height < 400:
                    logging.info("Image is too small (less than 400x400 pixels).")
                    os.remove(image_path)
                    logging.info(
                        "Image %s has been deleted because it is too small.", image_path
                    )
                    return False

                # If the image is valid, attempt to square it
                self.square_img(image_path)
                return True

        except UnidentifiedImageError as e:
            logging.error("Error processing the image: %s", e)
            os.remove(image_path)
            return False

    def square_img(self, image_path):
        """Resize the image to a square."""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                if width != height and (width > height * 1.05 or height > width * 1.05):
                    self.crop_image_to_square(image_path)
                else:
                    logging.info("Image already squared: %s", image_path)
                    return True
        except UnidentifiedImageError as e:
            logging.error("Error squaring the image: %s", e)
            os.remove(image_path)
            return False

    def crop_image_to_square(self, image_to_be_cropped):
        logging.info("crop_image_to_square : %s", image_to_be_cropped)
        try:
            with Image.open(image_to_be_cropped) as img:
                width, height = img.size
                logging.info(
                    "Cropping image %s from %dx%d to square",
                    image_to_be_cropped,
                    width,
                    height,
                )

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

                logging.info(
                    "Cropping image to: left=%s, top=%s, right=%s, bottom=%s",
                    left,
                    top,
                    right,
                    bottom,
                )

                im1 = img.crop((left, top, right, bottom))

                # Save the cropped image, overwriting the original
                im1.save(image_to_be_cropped, format="JPEG", quality=95, subsampling=2)

        except UnidentifiedImageError as e:
            logging.error("Error cropping image %s: %s", image_to_be_cropped, e)
            os.remove(image_to_be_cropped)
            return False
