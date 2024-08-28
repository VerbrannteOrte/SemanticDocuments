from surya.recognition import batch_recognition
from surya.layout import batch_layout_detection
from surya.detection import batch_text_detection
from surya.model.detection.model import (
    load_model as load_detection_model,
    load_processor as load_detection_processor,
)
from surya.model.recognition.model import load_model as load_recognition_model
from surya.model.recognition.processor import (
    load_processor as load_recognition_processor,
)
from surya.settings import settings as surya_settings

from semdoc.cache import cache_for
from semdoc.xmlrpc import remote


@cache_for("image", "languages")
@remote("surya_text_recognition")
def text_recognition(image, languages):
    model = load_recognition_model()
    processor = load_recognition_processor()
    predictions = batch_recognition([image], [languages], model, processor)
    return (predictions[0][0], predictions[1][0])


@cache_for("image")
@remote("surya_text_detection")
def text_detection(image):
    model = load_detection_model()
    processor = load_detection_processor()
    predictions = batch_text_detection([image], model, processor)
    return predictions[0]


@cache_for("image")
@remote("surya_layout_detection")
def layout_detection(image):
    model = load_detection_model(checkpoint=surya_settings.LAYOUT_MODEL_CHECKPOINT)
    processor = load_detection_processor(
        checkpoint=surya_settings.LAYOUT_MODEL_CHECKPOINT
    )
    line_predictions = text_detection(image)
    predictions = batch_layout_detection([image], model, processor, [line_predictions])
    return predictions[0]
