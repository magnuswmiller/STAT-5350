'''
art-translator.py

Description:
    This file serves as the entry point for the art description translation program.
    This file handles CLI argument parsing and all logic for end-to-end translation.

Author:
    Magnus Miller

Date Last Updated:
    01/20/26
'''

# Import Libraries
import argparse
import os
from fpdf import FPDF
from typing import Union, Tuple

# Import Files
from ocr import extract_itt
from translation import translate
from tts import create_wav
from parser import parse_text

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
    
    def normalize_lang(user_lang: str) -> dict:
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

def text_extract(source_path: str,
                 source_lang: str = "eng",
                 debug: bool = True,
                 ret_conf: bool = False):
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

def clean_text(raw_text: str, debug: bool):
    information = parse_text(raw_text, debug)
    return information

def translate_text(raw_life_info: str,
                   raw_title: str,
                   raw_medium: str,
                   raw_source: str,
                   raw_desc: str,
                   source_lang: str,
                   target_lang: str):

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

def cli_output(author: str,
               trans_life_info: str,
               trans_title: str,
               year: str,
               trans_medium: str,
               trans_source: str,
               trans_desc: str):

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

def pdf_output(author: str,
               trans_life_info: str,
               trans_title: str,
               year: str,
               trans_medium: str,
               trans_source: str,
               trans_desc: str,
               output_path):
    # Creating PDF
    print("\t* Creating PDF file.")
    pdf_out = FPDF()
    pdf_out.add_page()

    print("\t* Writing PDF output.")
    # Create Author Cell
    pdf_out.set_font(family="Arial", style="BI", size=20)
    pdf_out.cell(200, 10, txt=author, ln=1)
    
    # Create Life Info Cell
    pdf_out.set_font(family="Arial", style="", size=15)
    pdf_out.cell(200, 10, trans_life_info, ln=2)

    # Create Title Cell
    pdf_out.set_font(family="Arial", style="BI", size=20)
    pdf_out.cell(200, 10, txt=trans_title, ln=3)

    # Create Year Cell
    pdf_out.set_font(family="Arial", style="I", size=15)
    pdf_out.cell(200, 10, txt=year, ln=4)

    # Create Medium Cell
    pdf_out.set_font(family="Arial", style="I", size=12)
    pdf_out.cell(200, 10, txt=trans_medium, ln=5)

    # Create Source Cell
    pdf_out.set_font(family="Arial", style="I", size=12)
    pdf_out.cell(200, 10, txt=trans_source, ln=6)

    # Create Description Cell
    pdf_out.set_font(family="Arial", style="", size=15)
    pdf_out.cell(200, 10, txt=trans_desc, ln=4)

    # Save PDF output
    print("\t* Saving translated description PDF to /Output_Files/Translated_Desc.pdf for review.")
    pdf_out.output(output_path + "/Translated_Desc.pdf")

    return -1

def audio_output():
    create_wav()
    return -1

def main(image, source_lang, target_lang, audio_output, debug, ret_conf, cli, pdf):
    # Input Verification
    '''
    Need to verify input language is supported by translation
    Need to verify output language is supported by translation
    Need to verify output language is supported by TTS if requested
    Need Caches for OCR supported Languages
    Need Cache for Translate supported Languages
    '''
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
    trans_life_info, trans_title, trans_medium, trans_source, trans_desc = translate_text(information['life_info'],
                                                                                          information['title'],
                                                                                          information['medium'],
                                                                                          information['source'],
                                                                                          information['description'],
                                                                                          trans_source,
                                                                                          trans_target)
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
