import os

from pico2d import load_image

class Grass:
    def __init__(self):
        image_path = os.path.join(os.path.dirname(__file__), 'grass.png')
        self.image = load_image(image_path)

    def draw(self):
        self.image.draw(400, 30)

    def update(self):
        pass