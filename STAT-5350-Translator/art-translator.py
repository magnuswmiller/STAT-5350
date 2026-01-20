'''
art-translator.py

Description:
    This file serves as the entry point for the art description translation program.
    This file handles CLI argument parsing and all logic for end-to-end translation.

Author:
    Magnus Miller

Date Last Updated:
    01/19/26
'''

# Import Libraries
import argparse
import os
from ocr import extract_itt

# Import Files


def main(image, source_lang, target_lang, audio_output, debug, psm, ret_conf):
    # Input Verification
    '''
    Need to verify input language is supported by translation
    Need to verify output language is supported by translation
    Need to verify output language is supported by TTS if requested
    '''

    # Define Base File Path
    base_path = os.getcwd()

    # Define Source and Output File Paths
    source_path = base_path + image

    # TODO: Define output path

    # TODO: Image to Text Extraction
    raw_info = extract_itt(source_path, source_lang, debug, ret_conf, psm)
    if ret_conf:
        print("----- Extracted Text -----")
        print(raw_info[0])
        print("----- Average Confidence Level -----")
        print(f"{raw_info[1]:.2f}%")
    else:
        print("----- Extracted Text -----")
        print(raw_info)

    # TODO: Parse and Clean Raw Text

    #TODO: Cleaned Text Translation

    #TODO: Output Text to CLI

    #TODO: Output Text to Output Directory

    #TODO: Output .wav File to Output Directory if Requested

    

if __name__ == "__main__":
    # CLI Argument Parsing
    parser = argparse.ArgumentParser(description='Art Museum Description Translator.')
    parser.add_argument("--image", required=True, help="Path to source image.")
    parser.add_argument("--input-lang", required=True, default="en", help="Original description language.")
    parser.add_argument("--target-lang", default="fr", help="Target translation language")
    parser.add_argument("--audio-output", default=True, help="Output audio translation")
    parser.add_argument("--debug", default=False, help="Debug mode saves intermediate images")
    parser.add_argument("--psm", default=6, help="Page Segmentation Mode (3-13)")
    parser.add_argument("--ret-conf", default=False, help="Returns confidence level for OCR")
    args = parser.parse_args()

    if args.audio_output == "True":
        args.audio_output = 1
    else:
        args.audio_output = 0

    print("Arguments:")
    print(args)
    main(args.image, args.input_lang, args.target_lang, args.audio_output, args.debug, args.psm, args.ret_conf)
