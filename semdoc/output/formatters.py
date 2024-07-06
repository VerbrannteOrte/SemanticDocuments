from .xml import XMLFormatter
from .pdf import PdfExporter


def get_formatter(format):
    if format == "xml":
        return XMLFormatter
    elif format == "pdf":
        return PdfExporter
    else:
        raise ValueError(f"Destination format not supported: {format}")
