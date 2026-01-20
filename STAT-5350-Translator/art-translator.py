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

# Import Files
from ocr import extract_itt
from translation import translate
from tts import create_wav

def text_extract(source_path: str,
                 source_lang: str = "eng",
                 debug: bool = True,
                 ret_conf: bool = False,
                 psm: int = 6):
    raw_info = extract_itt(source_path, source_lang, debug, ret_conf, psm)

    if ret_conf and debug:
        print("----- Extracted Text -----")
        print(raw_info[0])
        print("----- Average Confidence Level -----")
        print(f"{raw_info[1]:.2f}%")
    else:
        print("----- Extracted Text -----")
        print(raw_info)
    return raw_info

def clean_text():
    return -1

def translate_text(raw_title: str,
                   raw_desc: str,
                   target_lang: str):
    print("* Translating title.")
    trans_title = translate(raw_title, target_lang)
    print("* Translating description.")
    trans_desc = translate(raw_desc, target_lang)
    return trans_title, trans_desc

def cli_output(trans_title: str,
               author: str,
               year: str,
               trans_desc: str):
    print(f"Piece Title: {trans_title}")
    print(f"Author: {author}")
    print(f"Year: {year}")
    print(f"Piece Description: {trans_desc}")
    return -1

def pdf_output(trans_title: str,
               author: str,
               year: str,
               trans_desc,
               avg_conf: float,
               output_path: str,
               ret_conf: bool = True):
    # Creating PDF
    print("* Creating PDF file.")
    pdf_out = FPDF()
    pdf_out.add_page()
    pdf_out.set_font("Arial", size=15)

    print("* Writing PDF output.")
    # Create Title Cell
    pdf_out.set_font(style="BI")
    pdf_out.cell(200, 10, txt=trans_title, ln=1)

    # Create Author Cell
    pdf_out.set_font(style="B")
    pdf_out.cell(200, 10, txt=author, ln=2)

    # Create Year Cell
    pdf_out.set_font(style="I")
    pdf_out.cell(200, 10, txt=year, ln=3)

    # Create Description Cell
    pdf_out.set_font(style="")
    pdf_out.cell(200, 10, txt=trans_desc, ln=4)

    # Create Confidence
    if ret_conf:
        pdf_out.set_font(style="B")
        pdf_out.cell(200, 10, txt=f"Average ITT Confidence: {avg_conf:.2f}%", ln=5)

    # Save PDF output
    print("* Saving translated description PDF to /Output_Files/Translated_Desc.pdf for review.")
    pdf_out.output(output_path + "/Translated_Desc.pdf")

    return -1

def audio_output():
    create_wav()
    return -1

def main(image, source_lang, target_lang, audio_output, debug, psm, ret_conf):
    # Input Verification
    '''
    Need to verify input language is supported by translation
    Need to verify output language is supported by translation
    Need to verify output language is supported by TTS if requested
    '''

    # Define File Paths
    base_path = os.getcwd()
    source_path = base_path + image
    output_path = base_path + "/Output_Files"

    # Image preprocessing and extraction
    print("Image Pre-Processing and Extraction Routine:")
    raw_info = text_extract(source_path, source_lang, debug, ret_conf, psm)
    avg_conf = 0.0
    if ret_conf:
        avg_conf = raw_info[1]

    '''
    # TODO: Parse and Clean Raw Text
    print("Parsing and Cleaning Routine:")
    author, life_info, raw_title, year, raw_med, raw_source, raw_desc = clean_text()

    # TODO: Cleaned Text Translation
    # Text translation
    print("Text translation Routine:")
    trans_title, trans_desc = translate_text(raw_title, raw_desc, target_lang)

    # Printing translated description plaque to CLI
    cli_output(trans_title, author, year, trans_desc)

    # Writing PDF output of translated description plaque
    print("PDF Output Routine:")
    pdf_output(trans_title, author, year, trans_desc, avg_conf, output_path, ret_conf)
    
    #TODO: Output .wav File to Output Directory if Requested
    print("Audio Output Routine:")
    audio_output()
    '''
    

if __name__ == "__main__":
    # CLI Argument Parsing
    parser = argparse.ArgumentParser(description='Art Museum Description Translator.')
    parser.add_argument("--image", required=True, help="Path to source image.")
    parser.add_argument("--input-lang", required=True, default="en", help="Original description language.")
    parser.add_argument("--target-lang", default="fr", help="Target translation language")
    parser.add_argument("--audio-output", default=True, help="Output audio translation")
    parser.add_argument("--debug", default=False, help="Debug mode saves intermediate images")
    parser.add_argument("--psm", default=6, help="Page Segmentation Mode (3-13)")
    parser.add_argument("--ret-conf", default=True, help="Returns confidence level for OCR")
    args = parser.parse_args()

    if args.audio_output == "True":
        args.audio_output = 1
    else:
        args.audio_output = 0

    print("Arguments:")
    print(args)
    main(args.image, args.input_lang, args.target_lang, args.audio_output, args.debug, args.psm, args.ret_conf)
