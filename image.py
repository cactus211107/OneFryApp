from PIL import Image
from pillow_heif import register_heif_opener
import datetime
from PIL.ExifTags import TAGS

def compress_image(input_path, output_path, quality = 80):
    register_heif_opener()
    image = Image.open(input_path)
    image.thumbnail((960,720))
    image.save(output_path, format="WebP", quality=quality)
    print(f"Image compressed and saved to {output_path}")