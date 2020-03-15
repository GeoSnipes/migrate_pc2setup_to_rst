from PIL import ImageFilter
import pytesseract
import path_location

import io
import json
import cv2
import numpy as np
import requests

import time
import re

from IPython.display import display as disp_img_inline

pytesseract.pytesseract.tesseract_cmd = path_location.TESSERACT_LOC

def image_convert(image):
    greyscale = image.convert('L')
    blackwhite = greyscale.point(lambda x: 0 if x < 200 else 255, '1')
    return image

def ocr(img, v1=False, raw=False):
    if v1:
        return pytesseract.image_to_string(img).split('\n')
    else:
        img.save("screenshot.jpg")
        img = cv2.imread("screenshot.jpg")
        url_api = "https://api.ocr.space/parse/image"
        _, compressedimage = cv2.imencode(".jpg", img, [1, 90])
        file_bytes = io.BytesIO(compressedimage)

        result = requests.post(url_api,
                    files = {"screenshot.jpg": file_bytes},
                    data = {"apikey": path_location.OCR_SPACE_API_KEY,
                            "language": "eng",'isOverlayRequired':raw})
        result = result.content.decode()
        result = json.loads(result)
        if raw:
            return result
        parsed_results = result.get("ParsedResults")[0]
        return parsed_results.get("ParsedText").split()

def retriev_ocr(content, debug=True):
    img=content
    results = ocr(content)
    content = []
    if len(results) == 0:
        content.append('1')
    else:
        for val in results:
            try:
                content.append(re.match('\\d+', val).group())
            except:
                content.append('0')
    if debug:
        disp_img_inline(img)
        print(f'{results}\t->\t{content}')
        print()
    return content
