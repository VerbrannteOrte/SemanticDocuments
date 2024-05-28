from .xml import XMLFormatter


def get_formatter(format):
    if format == "xml":
        return XMLFormatter
    else:
        raise ValueError(f"Destination format not supported: {format}")
