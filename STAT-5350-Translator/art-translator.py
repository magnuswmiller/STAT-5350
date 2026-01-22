'''
art-translator.py

Description:
    This file serves as the entry point for the art description translation program.
    This file handles CLI argument parsing and all logic for end-to-end translation.

Author:
    Magnus Miller

Date Last Updated:
    01/22/26
'''

# Import Libraries
import argparse
import os
from fpdf import FPDF
from typing import Union, Tuple, Dict, Any

# Import Files
from ocr import extract_itt
from translation import translate
from tts import create_wav
from parser import parse_text

'''
lang_converter()
Description:
    Converts language names or short codes to appropriate ISO codes for OCR or translation.
    Supports both 2-letter codes (for translation) and 3-letter codes (for OCR).
Args:
    mode (str) - Either 'ocr' or 'trans' to specify which code format to return
    source (str) - Source language name or code
    target (str, optional) - Target language name or code (only for 'trans' mode)
Return:
    str - OCR language code (3-letter) if mode is 'ocr'
    Tuple[str, str] - Tuple of (source, target) translation codes (2-letter) if mode is 'trans'
'''
def lang_converter(mode: str, source: str, target: str = None) -> Union[str, Tuple[str, str]]:
    # Mapping from common names/short codes to ISO 2-letter (for trans) and 3-letter (for ocr)
    lang_map = {
        # English
        'english': {'trans': 'en', 'ocr': 'eng'},
        'en': {'trans': 'en', 'ocr': 'eng'},
        
        # French
        'french': {'trans': 'fr', 'ocr': 'fra'},
        'fr': {'trans': 'fr', 'ocr': 'fra'},
        
        # German
        'german': {'trans': 'de', 'ocr': 'deu'},
        'de': {'trans': 'de', 'ocr': 'deu'},
        
        # Spanish
        'spanish': {'trans': 'es', 'ocr': 'spa'},
        'es': {'trans': 'es', 'ocr': 'spa'},
        
        # Italian
        'italian': {'trans': 'it', 'ocr': 'ita'},
        'it': {'trans': 'it', 'ocr': 'ita'},
        
        # Add more as needed...
        # Chinese (simplified)
        'chinese': {'trans': 'zh', 'ocr': 'chi_sim'},
        'zh': {'trans': 'zh', 'ocr': 'chi_sim'},
        
        # Japanese
        'japanese': {'trans': 'ja', 'ocr': 'jpn'},
        'ja': {'trans': 'ja', 'ocr': 'jpn'},
        
        # Russian
        'russian': {'trans': 'ru', 'ocr': 'rus'},
        'ru': {'trans': 'ru', 'ocr': 'rus'},
    }
    
    def normalize_lang(user_lang: str) -> Dict[str, str]:
        low_lang = user_lang.lower().strip()
        if low_lang in lang_map:
            return lang_map[low_lang]
        # Fallback: assume it's already a code
        for key, val in lang_map.items():
            if low_lang == val['trans'] or low_lang == val['ocr']:
                return val
        raise ValueError(f"Unsupported language: {user_lang}")
    
    if mode == "ocr":
        if target is not None:
            raise ValueError("Target lang not needed for OCR mode")
        return normalize_lang(source)['ocr']
    
    elif mode == "trans":
        if target is None:
            raise ValueError("Target lang required for trans mode")
        src_codes = normalize_lang(source)
        tgt_codes = normalize_lang(target)
        return (src_codes['trans'], tgt_codes['trans'])
    
    else:
        raise ValueError(f"Invalid mode: {mode}. Use 'ocr' or 'trans'.")

'''
text_extract()
Description:
    Extracts text from an image using OCR (Optical Character Recognition).
    Optionally returns confidence level of the extraction.
Args:
    source_path (str) - Path to the source image file
    source_lang (str) - Language code for OCR (default: "eng")
    debug (bool) - If True, prints extracted text and confidence to console
    ret_conf (bool) - If True, calculates and returns average confidence level
Return:
    Tuple[str, float] - Extracted text and average confidence level (or 0.0 if not requested)
'''
def text_extract(source_path: str,
                 source_lang: str = "eng",
                 debug: bool = True,
                 ret_conf: bool = False) -> Tuple[str, float]:
    extracted_text, avg_conf = extract_itt(source_path, source_lang, debug, ret_conf)

    if ret_conf == True and debug == True:
        print("----- Extracted Text -----")
        print(extracted_text)
        print("----- Average Confidence Level -----")
        print(f"{avg_conf:.2f}%")
    elif debug == True:
        print("----- Extracted Text -----")
        print(extracted_text)

    return extracted_text, avg_conf

'''
clean_text()
Description:
    Parses raw OCR-extracted text into structured fields for museum plaque information.
Args:
    raw_text (str) - Raw text extracted from OCR
    debug (bool) - If True, prints parsing information
Return:
    Dict[str, Any] - Dictionary containing parsed fields (author, title, year, etc.)
'''
def clean_text(raw_text: str, debug: bool) -> Dict[str, Any]:
    information = parse_text(raw_text, debug)
    return information

'''
translate_text()
Description:
    Translates all fields of the museum plaque from source language to target language.
Args:
    raw_life_info (str) - Artist's life information (birth-death dates)
    raw_title (str) - Title of the artwork
    raw_medium (str) - Medium/materials used
    raw_source (str) - Source/credit line
    raw_desc (str) - Description of the artwork
    source_lang (str) - Source language code
    target_lang (str) - Target language code
Return:
    Tuple[str, str, str, str, str] - Tuple of all translated fields in order
'''
def translate_text(raw_life_info: str,
                   raw_title: str,
                   raw_medium: str,
                   raw_source: str,
                   raw_desc: str,
                   source_lang: str,
                   target_lang: str) -> Tuple[str, str, str, str, str]:

    print("\t* Translating life info.")
    trans_life_info = translate(raw_life_info, source_lang, target_lang)
    print("\t* Translating title.")
    trans_title = translate(raw_title, source_lang, target_lang)
    print("\t* Translating medium.")
    trans_medium = translate(raw_medium, source_lang, target_lang)
    print("\t* Translating source.")
    trans_source = translate(raw_source, source_lang, target_lang)
    print("\t* Translating description.")
    trans_desc = translate(raw_desc, source_lang, target_lang)
    return trans_life_info, trans_title, trans_medium, trans_source, trans_desc

'''
cli_output()
Description:
    Prints the translated plaque information to the command line interface.
Args:
    author (str) - Artist's name
    trans_life_info (str) - Translated life information
    trans_title (str) - Translated artwork title
    year (str) - Year the artwork was created
    trans_medium (str) - Translated medium information
    trans_source (str) - Translated source/credit line
    trans_desc (str) - Translated description
Return:
    int - Returns -1 to indicate completion
'''
def cli_output(author: str,
               trans_life_info: str,
               trans_title: str,
               year: str,
               trans_medium: str,
               trans_source: str,
               trans_desc: str) -> int:

    print("\n\n\n\n\n")
    print("---------- Translation ----------")
    print(f"Author: {author}")
    print(f"Life Information: {trans_life_info}")
    print(f"Piece Title: {trans_title}")
    print(f"Year: {year}")
    print(f"Piece Medium: {trans_medium}")
    print(f"Piece Source: {trans_source}")
    print(f"Piece Description: {trans_desc}")

    return -1

'''
pdf_output()
Description:
    Creates a PDF file containing the translated plaque information with proper formatting.
Args:
    author (str) - Artist's name
    trans_life_info (str) - Translated life information
    trans_title (str) - Translated artwork title
    year (str) - Year the artwork was created
    trans_medium (str) - Translated medium information
    trans_source (str) - Translated source/credit line
    trans_desc (str) - Translated description
    output_path (str) - Directory path where PDF will be saved
Return:
    int - Returns -1 to indicate completion
'''
def pdf_output(author: str,
               trans_life_info: str,
               trans_title: str,
               year: str,
               trans_medium: str,
               trans_source: str,
               trans_desc: str,
               output_path: str) -> int:
    # Creating PDF
    print("\t* Creating PDF file.")
    pdf_out = FPDF()
    pdf_out.add_page()
    pdf_out.add_font(family="D-DIN", style='', fname="D-DIN.ttf")
    pdf_out.add_font(family="D-DIN", style='B', fname="D-DIN-Bold.ttf")
    pdf_out.add_font(family="D-DIN", style='I', fname="D-DIN-Italic.ttf")
    pdf_out.set_margins(left=1.0, right=1.0, top=1.0)

    print("\t* Writing PDF output.")
    # Create Author Cell
    pdf_out.set_font(family="D-DIN", style="B", size=20)
    pdf_out.cell(200, 10, text=author, new_x='LEFT', new_y='NEXT')
    
    # Create Life Info Cell
    pdf_out.set_font(family="D-DIN", style="", size=15)
    pdf_out.cell(200, 10, trans_life_info, new_x='LEFT', new_y='NEXT')

    # Create Title Cell
    pdf_out.set_font(family="D-DIN", style="B", size=20)
    pdf_out.cell(200, 10, text=trans_title, new_x='LEFT', new_y='NEXT')

    # Create Year Cell
    pdf_out.set_font(family="D-DIN", style="I", size=15)
    pdf_out.cell(200, 10, text=year, new_x='LEFT', new_y='NEXT')

    # Create Medium Cell
    pdf_out.set_font(family="D-DIN", style="I", size=12)
    pdf_out.cell(200, 10, text=trans_medium, new_x='LEFT', new_y='NEXT')

    # Create Source Cell
    pdf_out.set_font(family="D-DIN", style="I", size=12)
    pdf_out.cell(200, 10, text=trans_source, new_x='LEFT', new_y='NEXT')

    # Create Description Cell
    pdf_out.set_font(family="D-DIN", style="", size=15)
    pdf_out.multi_cell(200, 10, text=trans_desc, new_x='LEFT', new_y='NEXT')

    # Save PDF output
    print("\t* Saving translated description PDF to /Output_Files/Translated_Desc.pdf for review.")
    pdf_out.output(output_path + "/Translated_Desc.pdf")

    return -1

'''
audio_output()
Description:
    Creates an audio file (.wav) of the translated description (currently not implemented).
Args:
    None
Return:
    int - Returns -1 to indicate completion
'''
def audio_output() -> int:
    create_wav()
    return -1

'''
main()
Description:
    Main driver function that orchestrates the entire translation pipeline from OCR to output.
Args:
    image (str) - Path to the image file containing the plaque
    source_lang (str) - Source language of the plaque text
    target_lang (str) - Target language for translation
    audio_output (bool) - Whether to generate audio output
    debug (bool) - Whether to enable debug mode
    ret_conf (bool) - Whether to return OCR confidence levels
    cli (bool) - Whether to print output to CLI
    pdf (bool) - Whether to generate PDF output
Return:
    None
'''
def main(image: str, 
         source_lang: str, 
         target_lang: str, 
         audio_output: bool, 
         debug: bool, 
         ret_conf: bool, 
         cli: bool, 
         pdf: bool) -> None:
    # Normalizing languages
    ocr_source = lang_converter('ocr', source_lang)
    trans_langs = lang_converter('trans', source_lang, target_lang)
    trans_source = trans_langs[0]
    trans_target = trans_langs[1]

    # Define File Paths
    base_path = os.getcwd()
    source_path = base_path + image
    output_path = base_path + "/Output_Files"

    # Image preprocessing and extraction
    print("------------------------------")
    print("Image Pre-Processing and Extraction Routine:")
    extracted_text, avg_conf = text_extract(source_path, ocr_source, debug, ret_conf)
    print("------------------------------")

    # Parsing extracted text to fill fields
    print("------------------------------")
    print("Parsing and Cleaning Routine:")
    information = clean_text(extracted_text, debug)
    if information['parse_success'] != True:
        raise ValueError(f"Parser failed to find all fields:\n\t{information}")
    author = information['author']
    year = information['year']
    print("------------------------------")

    # Text translation
    print("------------------------------")
    print("Text translation Routine:")
    trans_life_info, trans_title, trans_medium, trans_source, trans_desc = translate_text(
        information['life_info'],
        information['title'],
        information['medium'],
        information['source'],
        information['description'],
        trans_source,
        trans_target
    )
    print("------------------------------")

    # Printing translated description plaque to CLI
    if cli:
        print("------------------------------")
        cli_output(author, trans_life_info, trans_title, year, trans_medium, trans_source, trans_desc)
        print("------------------------------")

    # Writing PDF output of translated description plaque
    if pdf:
        print("------------------------------")
        print("PDF Output Routine:")
        pdf_output(author, trans_life_info, trans_title, year, trans_medium, trans_source, trans_desc, output_path)
        print("------------------------------")
    
    '''
    #TODO: Output .wav File to Output Directory if Requested
    if audio_output:
        print("Audio Output Routine:")
        audio_output()
    '''
    

if __name__ == "__main__":
    # CLI Argument Parsing
    parser = argparse.ArgumentParser(description='Art Museum Description Translator.')
    parser.add_argument("--image", required=True, help="Path to source image.")
    parser.add_argument("--input-lang", required=True, default="en", help="Original description language.")
    parser.add_argument("--target-lang", default="fr", help="Target translation language")
    parser.add_argument("--audio-output", action='store_true', help="Output audio translation")
    parser.add_argument("--debug", action='store_true', help="Debug mode saves intermediate images")
    parser.add_argument("--ret-conf", action='store_true', help="Returns confidence level for OCR")
    parser.add_argument("--cli", action='store_true', help="Prints output to CLI")
    parser.add_argument("--pdf", action='store_true', help="Prints output to PDF")
    args = parser.parse_args()

    if args.debug:
        print("Arguments:")
        print("\t" + str(args))

    main(args.image, args.input_lang, args.target_lang, args.audio_output, args.debug, args.ret_conf, args.cli, args.pdf)