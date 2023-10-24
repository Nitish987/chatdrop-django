import json

from google.cloud import vision
from google.cloud.vision import Feature
from .debug import debug_print

class InvalidImageError(Exception):
    '''Invalid Image error'''
    def __init__(self, message='Invalid Image Error'):
        self.message = message
        super().__init__(self.message)



class ImageDetectionPrediction:
    '''Image Detection Prediction container.'''
    def __init__(self, is_safe=True, labels=[]):
        self.is_safe = is_safe
        self.labels = labels


class ImageDetection:
    '''Images processing using Google Vision API.'''

    def __init__(self):
        self.client = vision.ImageAnnotatorClient()

    @staticmethod
    def get_instance():
        return ImageDetection()

    def __load_image(self, image_bytes):
        image = vision.Image()
        image.content = image_bytes
        return image
    
    def __make_request(self, image):
        features = [Feature(type_=Feature.Type.LABEL_DETECTION), Feature(type_=Feature.Type.SAFE_SEARCH_DETECTION)]
        request = vision.AnnotateImageRequest(image=image, features=features)
        return request
    
    def __serialize_reponse(self, response: vision.AnnotateImageResponse):
        response_json = vision.AnnotateImageResponse.to_json(response)
        return json.loads(response_json)

    @staticmethod
    def process(image_bytes) -> ImageDetectionPrediction:
        '''
            1. requires io.bytesIO to process.
            2. extract labels according to objects found in image.
        '''
        image_bytes = image_bytes.read()
        processing = ImageDetection.get_instance()
        image = processing.__load_image(image_bytes)
        request = processing.__make_request(image=image)
        response = processing.client.annotate_image(request=request)
        response = processing.__serialize_reponse(response)
        
        is_safe = True
        if response['safeSearchAnnotation']['adult'] == vision.Likelihood.VERY_LIKELY:
            is_safe = False

        labels = []
        for label_dict in response['labelAnnotations']:
            if int(label_dict['score'] * 100) > 80:
                labels.append(str(label_dict['description']).lower())
        
        debug_print(is_safe)
        debug_print(labels)
        
        return ImageDetectionPrediction(is_safe=is_safe, labels=labels)