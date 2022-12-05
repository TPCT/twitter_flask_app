import random
import numpy as np
import cv2 as cv


class ImageRandomize:
    def __init__(self, image_bytes, padding=100):
        self._image_bytes = image_bytes
        self._padding = int(padding)
        self._return_image = None

    def randomize(self):
        try:
            image_numpy = np.fromstring(self._image_bytes, dtype='uint8')
            image_cv = cv.imdecode(image_numpy, cv.IMREAD_UNCHANGED)
            image_rgb = cv.cvtColor(image_cv, cv.COLOR_BGR2RGB)
            image_height, image_width, image_channels = image_rgb.shape
            new_image = np.full((image_height + self._padding, image_width + self._padding, image_channels),
                                (random.randint(0, 255),
                                 random.randint(0, 255),
                                 random.randint(0, 255)))
            padding = self._padding//2
            new_image[padding:image_height + padding, padding:image_width + padding] = image_rgb[:, :]
            self._return_image = cv.imencode('.png', new_image)[1]
            return self._return_image
        except Exception as e:
            print('[-] An error occurred in image_randomizer: ', e)

    @property
    def image(self):
        return self._return_image
