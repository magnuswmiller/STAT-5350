'''
ocr.py

Description:
    This file handles the Image to Text conversion. This file uses the tesseract-ocr library
    which uses a neural net (LTSM) based OCR engine. This file takes in images and converts the
    output to plain text.

Author:
    Magnus Miller

Date Last Updated:
    01/20/26
'''

# Import Libraries
import os
import numpy as np
import cv2
import pytesseract
from PIL import Image
from typing import Union, Tuple
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

'''
img_pre_pro()
Description: This function handles the pre-processing for OCR. This function converts the image to
             grayscale, applies small gaussian blur.
Args:
    source_path [str] - file path to image
    debug [bool] - Debug saves intermediate images
Return:
    Returns processed OpenCV image (BGR format)
'''

def img_pre_pro(source_path: str,
                   debug: bool = False
                   ) -> np.ndarray:

    # Check if image exists
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Image file not found: {source_path}.")

    # Load file
    pre_pro_img = cv2.imread(source_path)
    if pre_pro_img is None:
        raise ValueError("Image failed to load.")
    print("* Image successfully loaded.")

    # Convert image to grayscale
    gray_img = cv2.cvtColor(pre_pro_img, cv2.COLOR_BGR2GRAY)
    print("* Image converted to grayscale.")

    # Apply Gaussian blur
    gauss_img = cv2.GaussianBlur(gray_img, (3, 3), 0)
    print("* Gaussian blur applied.")

    # Apply thresholding
    thresh_img = cv2.threshold(gauss_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    print("* Image thresholding applied.")

    # Handle returns
    if debug:
        cv2.imwrite(os.getcwd() + "/Debug_Files/debug_preprocessed.png", thresh_img)
        print("* Saved debug_preprocessed.png for inspection.")

    return thresh_img

'''
run_ocr()
Description:
    This function handles running and interacting with the pytesseract ocr library. This
    function will extract the text from the PIL image if no confidence level is requested.
    If a confidence level is requested, the function will both extract the text from the PIL
    image as well as calculate the average confidence level for each line.
Args:
    pil_image [Image] - Pre-processed PIL image
    ocr_config [str] - Custom configuration for OCR use
    ret_conf [bool] - Returns text as well as confidence level
    debug [bool] - Prints average confidence level
'''
def run_ocr(source_lang: str, pil_img: Image, ret_conf: bool = False):
    if ret_conf:
        # Get detailed image data
        print("* Running OCR.")
        img_data = pytesseract.image_to_data(pil_img, lang=source_lang, output_type=pytesseract.Output.DICT)

        text_lines = []
        confidences = []

        # Extract text and confidences
        print("* Extracting data from image.")
        for i in range(len(img_data["text"])):
            if int(img_data["conf"][i]) != -1 and img_data["text"][i].strip():
                text_lines.append(img_data["text"][i])
                confidences.append(float(img_data["conf"][i]))
        
        extracted_text = " ".join(text_lines).strip()
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return [extracted_text, avg_conf]
    else:
        print("* Running OCR.")
        extracted_text = pytesseract.image_to_string(pil_img, lang=source_lang).strip()

        return [extracted_text, None]

'''
extract_itt()
Description: This function uses the tesseract ocr library to handle converting the provided
             image to text. The function serves as a driver and preprocesses the image before
             using the library.
Args:
    source_path [str] - file path to image
    source_lang [str] - language of source text (Def: "eng")
    psm [int] - Page Segmentation Mode (3-13)
    debug [bool] - Debug mode saves intermediate images
    ret_conf [bool] - Returns text as well as confidence level
Return:
    Returns extracted text (str) or extracted text and confidence if requested (str, float)
    as tuple.
'''
def extract_itt(source_path: str,
                source_lang: str,
                debug: bool = False,
                ret_conf: bool = False,
                psm: int = 6,
                ) -> Union[str, Tuple[str, float]]:
    
    # Pre-process source image
    pre_pro_img = img_pre_pro(source_path, debug)

    # Convert pre-processed image to PIL
    print("* Converting image array to PIL")
    pil_img = Image.fromarray(pre_pro_img)

    # Run OCR
    print("Image OCR Routine:")
    extracted_text, avg_conf = run_ocr(source_lang, pil_img, ret_conf)

    # Handle Returns
    if ret_conf:
        return extracted_text, avg_conf
    else:
        return extracted_text
