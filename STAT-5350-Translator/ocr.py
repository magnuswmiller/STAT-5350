'''
ocr.py

Description:
    This file handles the Image to Text conversion. This file uses the tesseract-ocr library
    which uses a neural net (LTSM) based OCR engine. This file takes in images and converts the
    output to plain text.

Author:
    Magnus Miller

Date Last Updated:
    01/22/26
'''

# Import Libraries
import os
import numpy as np
import cv2
import pytesseract
from PIL import Image
from typing import Union, Tuple, List
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'

'''
img_pre_pro()
Description:
    This function handles the pre-processing for OCR. This function converts the image to
    grayscale, applies small gaussian blur, and applies thresholding for better OCR accuracy.
Args:
    source_path (str) - File path to image
    debug (bool) - Debug saves intermediate images to Debug_Files directory
Return:
    np.ndarray - Processed OpenCV image array (grayscale with thresholding applied)
'''
def img_pre_pro(source_path: str,
                debug: bool = False) -> np.ndarray:

    # Check if image exists
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"Image file not found: {source_path}.")

    # Load file
    pre_pro_img = cv2.imread(source_path)
    if pre_pro_img is None:
        raise ValueError("Image failed to load.")
    print("\t* Image successfully loaded.")

    # Convert image to grayscale
    gray_img = cv2.cvtColor(pre_pro_img, cv2.COLOR_BGR2GRAY)
    print("\t* Image converted to grayscale.")

    # Apply Gaussian blur
    gauss_img = cv2.GaussianBlur(gray_img, (3, 3), 0)
    print("\t* Gaussian blur applied.")

    # Apply thresholding
    thresh_img = cv2.threshold(gauss_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    print("\t* Image thresholding applied.")

    # Handle returns
    if debug:
        cv2.imwrite(os.getcwd() + "/Debug_Files/debug_preprocessed.png", thresh_img)
        print("\t* Saved debug_preprocessed.png for inspection.")

    return thresh_img

'''
run_ocr()
Description:
    This function handles running and interacting with the pytesseract ocr library. This
    function will extract the text from the PIL image. If confidence level is requested,
    the function will both extract the text and calculate the average confidence level
    for each line.
Args:
    source_lang (str) - Language code for OCR (e.g., 'eng', 'fra', 'deu')
    pil_img (Image) - Pre-processed PIL image
    ret_conf (bool) - If True, returns text and confidence level; if False, returns text only
Return:
    List[Union[str, float]] - List containing [extracted_text, avg_conf] where avg_conf is
                              float if ret_conf=True, or None if ret_conf=False
'''
def run_ocr(source_lang: str, pil_img: Image, ret_conf: bool = False) -> List[Union[str, float]]:
    
    if ret_conf == True:
        # Get detailed image data
        print("\t* Running OCR with --oem 3 --psm 4.")
        img_data = pytesseract.image_to_data(pil_img, lang=source_lang, output_type=pytesseract.Output.DICT)

        text_lines = []
        confidences = []

        # Extract text and confidences
        print("\t* Extracting data from image.")
        for i in range(len(img_data["text"])):
            if int(img_data["conf"][i]) != -1 and img_data["text"][i]:
                text_lines.append(img_data["text"][i])
                confidences.append(float(img_data["conf"][i]))
        extracted_text = " ".join(text_lines)
        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        return [extracted_text, avg_conf]
    else:
        print("\t* Running OCR.")
        extracted_text = pytesseract.image_to_string(pil_img, lang=source_lang)

        return [extracted_text, None]

'''
extract_itt()
Description:
    This function uses the tesseract ocr library to handle converting the provided
    image to text. The function serves as a driver and preprocesses the image before
    using the library.
Args:
    source_path (str) - File path to image
    source_lang (str) - Language of source text (e.g., 'eng', 'fra', 'deu')
    debug (bool) - Debug mode saves intermediate images to Debug_Files directory
    ret_conf (bool) - If True, returns text and confidence level; if False, returns text only
Return:
    Tuple[str, float] - Tuple containing (extracted_text, avg_conf) where avg_conf is the
                        average confidence level as a float (0-100) if ret_conf=True, or 0.0
                        if ret_conf=False
'''
def extract_itt(source_path: str,
                source_lang: str,
                debug: bool = False,
                ret_conf: bool = False) -> Tuple[str, float]:
    
    # Pre-process source image
    pre_pro_img = img_pre_pro(source_path, debug)

    # Convert pre-processed image to PIL
    print("\t* Converting image array to PIL")
    pil_img = Image.fromarray(pre_pro_img)

    # Run OCR
    extracted_text, avg_conf = run_ocr(source_lang, pil_img, ret_conf)

    # Handle Returns
    if ret_conf:
        return extracted_text, avg_conf
    else:
        return extracted_text, avg_conf