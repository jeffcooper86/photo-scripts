import os
import re
import multiprocessing
import colors
import sys
import shutil
from PIL import Image

#*** Helper functions.
# Loop each directory containing photos to print.
def do_images():
    for to_print_d in directories_to_print:
        path = photos_path + to_print_d

        # Log status.
        print 'Parsing ' + path

        # Run in parallel processes for each photo.
        print_jobs = multiprocessing.Pool()
        for root, dirs, files in os.walk(photos_path + to_print_d):

            # If there are no subdirectories format the photos in that directory.
            if not len(dirs):

                # Log status.
                print 'Making photo versions for %s' % root
                print_jobs.apply_async(
                    make_photo_versions, args=(root, photo_name_after)
                )
        print_jobs.close()
        print_jobs.join()

def get_image_size_with_border(print_size, border_ratio, orientation):

    # Preserve 2:3 aspect ratio
    long_side = max(print_size[0], print_size[1]) * (1 - border_ratio)
    short_side = 2.0 / 3 * long_side
    image_size = tuple((int(long_side), int(short_side)))
    if orientation == 'portrait':
        return tuple(reversed(image_size))
    return image_size

def get_orientation(image):
    size = image.size
    if size[0] == size[1]:
        return 'square'
    elif size[0] > size[1]:
        return 'landscape'
    return 'portrait'

def get_print_size_in_pixels(ratio_in_inches, orientation):

    # 300 dpi.
    print_size = tuple(300 * x for x in ratio_in_inches)

    # Match the print orientation to the image. Square defaults to portrait.
    if orientation == 'landscape':
        print_size = tuple(reversed(print_size))
    return print_size

def getSourceImage(image_path):

    # Get the original jpg filename from the directory.
    return image_path + '/' + [f for f in os.listdir(image_path) \

        # Match files named like 'IMG_2234.jpg'.
        if re.match(r'^IMG_[0-9]+.*\.jpg$', f) \

        # Match files named like '2013-08-04 19.46.38.jpg'.
        or re.match(r'^([0-9]+[\-\.\s]?)+\.jpg$', f)][0]

def make_photo_versions(image_path, scope_from):

    # Make the scoped name for the photo print files.
    print_name = '_'.join(
        image_path[image_path.find(scope_from) + len(scope_from) + 1:]
        .replace(' ', '-').strip('/').split('/')[1:]
    )

    # Get the source image.
    original_image = None
    try:
        original_image = Image.open(getSourceImage(image_path))
    except:
        print colors.red('ERROR: No image found for %s' % image_path)

    # Save versions.
    if original_image:
        save_small_image(original_image, small_size, image_path)
        save_print_sizes(print_sizes, original_image, prints_path, print_name)

def make_print_with_border(image, size):
    border_color = (255, 255, 255)
    border_ratio = 0.25
    print_size = get_print_size_in_pixels(size, get_orientation(image))
    bordered_image_size = get_image_size_with_border(
        print_size, border_ratio, get_orientation(image))

    # Resize the image.
    resized_image = resize_image(image, bordered_image_size)

    # Make a new image and paste the resized image in it.
    bordered_image = Image.new('RGB', print_size, border_color)
    image_offset_for_border = (
        (print_size[0] - bordered_image_size[0]) / 2,
        (print_size[1] - bordered_image_size[1]) / 2
    )
    bordered_image.paste(resized_image, image_offset_for_border)
    return bordered_image

def resize_image(image, size):
    return image.resize(size, Image.ANTIALIAS)

def save_bordered_image(image, size, prints_path, print_name):
    size_string = 'x'.join(str(i) for i in size)
    size_path = prints_path + size_string + '/'
    if not os.path.exists(size_path):

        # Log status.
        print 'Making directory at ' + size_path
        os.makedirs(size_path)

    full_name = print_name + '_' + size_string + '.jpg'
    make_print_with_border(image, size).save(size_path + full_name)

    # Log status.
    print colors.green('Saved ' + full_name)

def save_small_image(image, small_size, image_path):
    if get_orientation(image) == 'landscape':
        small_size = tuple(reversed(small_size))
    resize_image(image, small_size).save(image_path + '/small.jpg')

    # Log status.
    print colors.green('Saved small copy to ' + image_path)

def save_print_sizes(print_sizes, image, prints_path, print_name):
    if not os.path.exists(prints_path):

        # Log status.
        print 'Making directory at ' + prints_path
        os.makedirs(prints_path)

    # Log status.
    print 'Saving print sizes for ' + print_name + ' to ' + prints_path
    for size in print_sizes:
        save_bordered_image(image, size, prints_path, print_name)

#*** Settings.
print_sizes = [
    (5, 7),
    (8, 10),
    (10, 12),
    (11, 14),
    (16, 20),
    (20, 30)]
small_size = (667, 1000)
photos_path = os.path.expanduser('~') + '/Dropbox/Photography/'
photo_name_after = 'Photography'
directories_to_print = ['_random', '_studio', 'location']

# Be careful changing this location as everything in it will be deleted.
prints_path = os.path.expanduser('~') + '/Pictures/Prints/'

# Pass currdir to only format photos within a directory instead of all of them.
if len(sys.argv) > 1 and sys.argv[1] == 'currdir':
    cwd = os.getcwd()

    # Still want to be within the photos directory.
    if cwd.find(photos_path) > -1:
        photos_path = cwd + '/'
        directories_to_print = [d for d in os.listdir('.') if os.path.isdir(d)]

# Remove the old prints before saving the new ones.
else:
    shutil.rmtree(prints_path)

#*** Parse photos directory and make versions for each photo.
do_images()
