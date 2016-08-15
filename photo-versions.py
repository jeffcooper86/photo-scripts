from PIL import Image

image_sizes = [
    (5, 7),
    (8, 10),
    (10, 12),
    (11, 14),
    (16, 20),
    (20, 30)]

# Open original image
original_image = Image.open('glacier/IMG_8962 (2).jpg')
original_size = original_image.size

# 300 dpi prints
print_size = tuple(300 * x for x in image_sizes[0])

if original_size[0] > original_size[1]:
     print_size = tuple(reversed(print_size))

# Resize original image for print size with a border
picture_size = tuple(int(0.75 * x) for x in print_size)
print picture_size
resized_image = original_image.resize(picture_size, Image.ANTIALIAS)

# Place resized image in new image with border
border_size = (
    (print_size[0] - picture_size[0]) / 2,
    (print_size[1] - picture_size[1]) / 2
    )

new_image = Image.new("RGB", print_size, (255, 255, 255))
new_image.paste(resized_image, border_size)

new_image.show()
# new_image.save('test.jpg')
