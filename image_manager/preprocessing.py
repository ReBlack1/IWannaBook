from PIL import Image


def resize_image(input_image_path,
                 output_image_path,
                 size=(512, 256)):
    original_image = Image.open(input_image_path)
    width, height = original_image.size
    print('The original image size is {wide} wide x {height} '
          'high'.format(wide=width, height=height))

    resized_image = original_image.resize(size)
    width, height = resized_image.size
    print('The resized image size is {wide} wide x {height} '
          'high'.format(wide=width, height=height))
    resized_image.show()
    resized_image.save(output_image_path, "png")


if __name__ == '__main__':
    resize_image(input_image_path='6.jpg',
                 output_image_path='fon_small.png',
                 size=(512, 256))
