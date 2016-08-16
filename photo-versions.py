import os
import re
from PIL import Image

#*** Settings.
print_sizes = [
    (5, 7),
    (8, 10),
    (10, 12),
    (11, 14),
    (16, 20),
    (20, 30)]
small_size = (667, 1000)
image_path = os.path.expanduser('~') \
    + '/Documents/development/photo-scripts/sample/'
prints_path = os.path.expanduser('~') + '/Pictures/Prints'

#*** Helper functions.
def get_image_size_with_border(print_size, border_ratio):

    # Preserve 2:3 aspect ratio
    long_side = max(print_size[0], print_size[1]) * (1 - border_ratio)
    short_side = 2.0 / 3 * long_side
    return (int(long_side), int(short_side))

def get_orientation(image):
    size = image.size
    if size[0] == size[1]:
        return 'square'
    elif size[0] > size[1]:
        return 'landscape'
    return 'portrait'

def get_print_size_in_pixels(ratio_in_inches):

    # 300 dpi.
    print_size = tuple(300 * x for x in ratio_in_inches)

    # Match the print orientation to the image. Square defaults to portrait.
    if get_orientation(original_image) == 'landscape':
        print_size = tuple(reversed(print_size))
    return print_size

def getSourceImage(image_path):

    # Get the original jpg filename from the directory.
    return image_path + [f for f in os.listdir(image_path) \
        if re.match(r'IMG_[0-9]+.*\.jpg', f)][0]

def make_print_with_border(image, print_size):
    border_color = (255, 255, 255)
    border_ratio = 0.25
    bordered_image_size = get_image_size_with_border(print_size, border_ratio)
    resized_image = resize_image(image, bordered_image_size)
    image_offset_for_border = (
        (print_size[0] - bordered_image_size[0]) / 2,
        (print_size[1] - bordered_image_size[1]) / 2
    )

    # Make a new image and paste the resized image in it.
    bordered_image = Image.new("RGB", print_size, border_color)
    bordered_image.paste(resized_image, image_offset_for_border)
    return bordered_image

def resize_image(image, size):
    return image.resize(size, Image.ANTIALIAS)

def save_bordered_image(image, print_size, prints_path):
    size_string = "x".join(str(i) for i in print_size)
    print_size = get_print_size_in_pixels(print_size)
    make_print_with_border(image, print_size).save(
        prints_path + '/bordered-print-' + size_string + '.jpg')

    # Log status.
    print "Saved " + size_string + " print"

def save_small_image(image, small_size, image_path):
    if get_orientation(image) == 'landscape':
        small_size = tuple(reversed(small_size))
    resize_image(original_image, small_size).save(image_path + '/small.jpg')

    # Log status.
    print "Saved small copy to " + image_path

def save_print_sizes(print_sizes, image, prints_path):
    if not os.path.exists(prints_path):

        # Log status.
        print "Making directory at " + prints_path
        os.makedirs(prints_path)

    # Log status.
    print "Saving print sizes to " + prints_path

    for size in print_sizes:
        save_bordered_image(image, size, prints_path)


#*** Make the photo versions.
# Get the source image.
original_image = Image.open(getSourceImage(image_path))

# Save a small version for previews.
save_small_image(original_image, small_size, image_path)

# Save bordered images for prints.
save_print_sizes(print_sizes, original_image, prints_path)
