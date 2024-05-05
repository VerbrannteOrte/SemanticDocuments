import pytesseract


class TesseractBlock:
    def __init__(self, level, left, top, width, height, conf, text):
        self.level = level
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.conf = conf
        self.text = text
        self.children = []

    def __repr__(self):
        return f"TB({self.level}, {repr(self.children)})"

    def add(self, block):
        self.children.append(block)


def to_block(data, i):
    return TesseractBlock(
        level=data["level"][i],
        left=data["left"][i],
        top=data["top"][i],
        width=data["width"][i],
        height=data["height"][i],
        conf=data["conf"][i],
        text=data["text"][i],
    )


def run_tesseract(img):
    lang = "deu"
    config = "--psm 3"
    data = pytesseract.image_to_data(
        img,
        lang=lang,
        config=config,
        output_type=pytesseract.Output.DICT,
    )
    pages = []
    page = None
    block = None
    par = None
    line = None
    page_num = 0
    block_num = 0
    par_num = 0
    line_num = 0
    for i in range(len(data["text"])):
        if page_num != data["page_num"][i]:
            page = to_block(data, i)
            pages.append(page)
            page_num = data["page_num"][i]
            block_num = 0
            par_num = 0
            line_num = 0
            continue
        if block_num != data["block_num"][i]:
            block = to_block(data, i)
            page.add(block)
            block_num = data["block_num"][i]
            par_num = 0
            line_num = 0
            continue
        if par_num != data["par_num"][i]:
            par = to_block(data, i)
            block.add(par)
            par_num = data["par_num"][i]
            line_num = 0
            continue
        if line_num != data["line_num"][i]:
            line = to_block(data, i)
            par.add(line)
            line_num = data["line_num"][i]
            continue
        word = to_block(data, i)
        line.add(word)

    return pages
