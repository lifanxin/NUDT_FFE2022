from PIL import Image


class IMGHelper():

    @staticmethod
    def save_img(img_data, file_path):
        img_data = img_data * 255
        img = Image.fromarray(img_data)
        img.save(file_path)

    @staticmethod
    def show_img(img_data):
        img = Image.fromarray(img_data)
        img.show()
