from semdoc.analyzer import Sequential, TreeOrganizer, Logicalizer, Tablelizer
from semdoc.analyzer import surya
from semdoc.analyzer.tidier import HeadingLevelCondenser, NonBlockWrapper


def semdoc_pipeline():
    ocr_pipeline = Sequential()
    text_detector = surya.TextLines()
    ocr_pipeline.add(text_detector)
    text_recognizer = surya.OCR()
    ocr_pipeline.add(text_recognizer)
    layout_recognizer = surya.Layout()
    ocr_pipeline.add(layout_recognizer)

    logical_pipeline = Sequential()
    organizer = TreeOrganizer()
    logical_pipeline.add(organizer)
    tablelizer = Tablelizer()
    logical_pipeline.add(tablelizer)
    logicalizer = Logicalizer()
    logical_pipeline.add(logicalizer)
    heading_level_condenser = HeadingLevelCondenser()
    logical_pipeline.add(heading_level_condenser)
    non_block_wrapper = NonBlockWrapper()
    logical_pipeline.add(non_block_wrapper)

    semdoc_pipeline = Sequential()
    semdoc_pipeline.add(ocr_pipeline)
    semdoc_pipeline.add(logical_pipeline)

    return semdoc_pipeline
