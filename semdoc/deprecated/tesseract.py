import sys
import pytesseract
from rich import pretty
import cv2
import seaborn
import copy


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
        return f"TB({self.level}:{self.left}.{self.top}:{self.width}.{self.height}, {repr(self.children)})"

    def add(self, block):
        self.children.append(block)

    def _visualize(self, img):
        steps = self.level - 1
        color = (255 - 63 * steps, 100 + 38 * steps, 0)
        colormap = seaborn.color_palette()
        color = [round(c * 255) for c in colormap[self.level]]
        pos1 = (self.left, self.top)
        pos2 = (self.left + self.width, self.top + self.height)
        cv2.rectangle(img, pos1, pos2, color, 1)

    def visualize_boundaries(self, img, level=0):
        if self.level == level or level == 0:
            self._visualize(img)
        for child in self.children:
            child.visualize_boundaries(img, level=level)


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


def run():
    img = cv2.imread(sys.argv[1])
    pages = run_tesseract(img)
    pretty.pprint(pages, expand_all=True)

    level_descriptors = [
        "page",
        "block",
        "paragraph",
        "line",
        "word",
    ]
    for level in range(1, 6):
        for page in pages:
            level_img = copy.copy(img)
            page.visualize_boundaries(level_img, level=level)
            caption = f"Level {level_descriptors[level - 1]}"
            cv2.imshow(caption, level_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
