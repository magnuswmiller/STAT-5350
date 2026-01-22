'''
parser.py

Description:
    This file parses the raw OCR-extracted text from a museum plaque
    and attempts to split it into structured fields based on common layout:
    Author, Life information, Title, Date produced, Medium, Source/Credit line, Description.

    Uses simple line-based heuristics + keyword detection.
    Not perfect for every plaque, but works well for standard formats.

Author:
    Magnus Miller

Date Last Updated:
    01/22/26
'''

# Importing Libraries
import re
from typing import Dict, Any

'''
parse_text()
Description:
    Parses raw OCR output into structured plaque fields. Uses line-based parsing to extract
    information in a typical museum plaque format: author name, life dates, artwork title,
    year created, medium, source/credit line, and description.
Args:
    raw_text (str) - The full text string returned from OCR
    debug (bool) - If True, prints intermediate parsing steps to console
Return:
    Dict[str, Any] - Dictionary containing the following keys:
        - 'author' (str): Artist's name
        - 'life_info' (str): Artist's life dates (e.g., "1881-1973")
        - 'title' (str): Title of the artwork
        - 'year' (str): Year artwork was created (e.g., "1923")
        - 'medium' (str): Medium/materials used
        - 'source' (str): Credit line/provenance
        - 'description' (str): Description of the artwork
        - 'parse_success' (bool): Whether parsing found all required fields
        - 'raw_text' (str): Original unprocessed text for reference
'''
def parse_text(raw_text: str, debug: bool) -> Dict[str, Any]:
    # Define information dictionary
    information: Dict[str, Any] = {
        'author': '',
        'life_info': '',
        'title': '',
        'year': '',
        'medium': '',
        'source': '',
        'description': '',
        'parse_success': False,
        'raw_text': raw_text
    }
    
    # Check if text has been passed
    if not raw_text.strip():
        if debug:
            print("\t* No text provided to parse and clean.")
        return information
    
    lines = [line.strip() for line in raw_text.split('\n')]
    
    print("\t* Parsing extracted text.")
    last_line_blank = True
    for i in range(len(lines)):
        if lines[i] != '':
            if information['author'] == '':
                information['author'] = lines[i]
                last_line_blank = False
            elif information['life_info'] == '' and last_line_blank == False:
                information['life_info'] = lines[i]
                last_line_blank = False
            elif information['title'] == '' and last_line_blank == True:
                information['title'] = lines[i]
                last_line_blank = False
            elif information['year'] == '' and last_line_blank == False:
                information['year'] = lines[i]
                last_line_blank = False
            elif information['medium'] == '' and last_line_blank == True:
                information['medium'] = lines[i]
                last_line_blank = False
            elif information['source'] == '' and last_line_blank == True:
                information['source'] = lines[i]
                last_line_blank = False
            elif information['description'] == '' and last_line_blank == True:
                information['description'] = lines[i]
                last_line_blank = False
            elif information['description'] != '' and last_line_blank == False:
                information['description'] = information['description'] + '\n' + lines[i]
                last_line_blank = False
        else:
            last_line_blank = True

    if all(value != '' for value in information.values()):
        print("\t* Successfully parsed extracted text. All fields collected.")
        information['parse_success'] = True

    return information