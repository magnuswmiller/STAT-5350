# Art Museum Description Plaque Translator

A Python-based tool that uses Optical Character Recognition (OCR) and machine translation to extract text from museum art plaques and translate them into different languages. The tool can output translations to CLI, PDF, and (planned) audio formats.

## Author
Magnus Miller

## Project Overview

This project automates the process of translating art museum description plaques by:

1. **Extracting text** from plaque images using Tesseract OCR
2. **Parsing** the extracted text into structured fields (author, title, dates, description, etc.)
3. **Translating** each field into a target language using HuggingFace transformers
4. **Outputting** the translated information in various formats (CLI, PDF, audio)

## Features

- **Multi-language OCR support**: English, French, German, Spanish, Italian, Chinese, Japanese, Russian
- **Neural translation**: Uses Helsinki-NLP opus-mt models or NLLB multilingual models
- **Structured parsing**: Automatically identifies and separates plaque components
- **Multiple output formats**: CLI display and PDF generation
- **Debug mode**: Saves intermediate images and displays confidence scores
- **GPU acceleration**: Automatically uses GPU if available for faster translation

## Requirements

### System Dependencies

#### Tesseract OCR
This project requires Tesseract OCR to be installed on your system.

**macOS (using Homebrew):**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from [Tesseract's GitHub releases](https://github.com/tesseract-ocr/tesseract/releases)

#### Language Data Files
For languages other than English, install additional Tesseract language packs:

**macOS:**
```bash
brew install tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-spa  # Spanish
# etc.
```

### Python Dependencies

Install Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### Required Font Files (for PDF output)

The PDF output requires the D-DIN font family. Place the following font files in your project root directory:
- `D-DIN.ttf` (regular)
- `D-DIN-Bold.ttf` (bold)
- `D-DIN-Italic.ttf` (italic)

## Installation

1. Clone or download this repository
2. Install system dependencies (Tesseract OCR)
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create the required directories:
   ```bash
   mkdir -p Output_Files Debug_Files
   ```
5. Add D-DIN font files to the project root (for PDF output)

## Usage

### Basic Command Structure

```bash
python art-translator.py --image <path> --input-lang <lang> --target-lang <lang> [options]
```

### Required Arguments

- `--image`: Path to the image file containing the art description plaque
  - Example: `--image /Input_Images/plaque.jpg`
  
- `--input-lang`: Original language of the plaque text
  - Accepts: full names (e.g., "english", "french") or ISO codes (e.g., "en", "fr")
  - Supported: English, French, German, Spanish, Italian, Chinese, Japanese, Russian

### Optional Arguments

- `--target-lang`: Target language for translation (default: "fr")
  - Same format as `--input-lang`
  
- `--cli`: Print the translated output to the command line interface
  
- `--pdf`: Generate a PDF file with the translated plaque information
  - Output saved to: `Output_Files/Translated_Desc.pdf`
  
- `--debug`: Enable debug mode
  - Saves preprocessed images to `Debug_Files/debug_preprocessed.png`
  - Prints detailed information during execution
  
- `--ret-conf`: Display OCR confidence levels
  - Shows average confidence score for text extraction
  
- `--audio-output`: Generate audio translation (currently not implemented)

### Example Commands

**Basic translation (English to French, PDF output):**
```bash
python art-translator.py --image /Input_Images/monet_plaque.jpg --input-lang en --target-lang fr --pdf
```

**Translation with CLI output and debug mode:**
```bash
python art-translator.py --image /Input_Images/picasso.jpg --input-lang spanish --target-lang english --cli --debug
```

**Translation with confidence scores:**
```bash
python art-translator.py --image /Input_Images/plaque.jpg --input-lang en --target-lang de --pdf --ret-conf --debug
```

**Multiple outputs:**
```bash
python art-translator.py --image /Input_Images/artwork.jpg --input-lang italian --target-lang english --cli --pdf --debug
```

## Project Structure

```
art-translator/
├── art-translator.py    # Main entry point and CLI argument parsing
├── ocr.py              # OCR image processing and text extraction
├── parser.py           # Text parsing into structured fields
├── translation.py      # Neural machine translation
├── tts.py              # Text-to-speech (not yet implemented)
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── Input_Images/      # Place source images here
├── Output_Files/      # Generated PDFs saved here
├── Debug_Files/       # Debug images saved here (if --debug enabled)
├── D-DIN.ttf          # Required font files for PDF
├── D-DIN-Bold.ttf
└── D-DIN-Italic.ttf
```

## How It Works

### 1. Image Preprocessing (`ocr.py`)
- Loads the input image
- Converts to grayscale
- Applies Gaussian blur to reduce noise
- Applies Otsu's thresholding for better OCR accuracy

### 2. Text Extraction (`ocr.py`)
- Uses Tesseract OCR with neural network engine
- Extracts text with optional confidence scoring
- Returns raw text string

### 3. Text Parsing (`parser.py`)
- Analyzes line breaks and spacing patterns
- Identifies structured fields:
  - Author name
  - Life information (birth-death dates)
  - Artwork title
  - Year created
  - Medium/materials
  - Source/credit line
  - Description

### 4. Translation (`translation.py`)
- Translates each field individually
- Uses Helsinki-NLP opus-mt models for specific language pairs
- Falls back to NLLB multilingual model if needed
- Leverages GPU acceleration when available

### 5. Output Generation
- **CLI**: Formatted text output to console
- **PDF**: Professionally formatted document with multiple fonts and styles
- **Audio**: Planned feature for accessibility

## Supported Languages

| Language | Full Name | OCR Code | Translation Code |
|----------|-----------|----------|------------------|
| English  | english   | eng      | en               |
| French   | french    | fra      | fr               |
| German   | german    | deu      | de               |
| Spanish  | spanish   | spa      | es               |
| Italian  | italian   | ita      | it               |
| Chinese  | chinese   | chi_sim  | zh               |
| Japanese | japanese  | jpn      | ja               |
| Russian  | russian   | rus      | ru               |

## Limitations

- Parsing assumes a standard museum plaque format with specific line breaks
- Translation quality depends on HuggingFace model availability for language pairs
- OCR accuracy depends on image quality, lighting, and text clarity
- First run will be slower while models are downloaded and cached

## Troubleshooting

**Issue: "tesseract_cmd not found"**
- Solution: Update the path in `ocr.py` line 18 to match your Tesseract installation:
  ```python
  pytesseract.pytesseract.tesseract_cmd = '/path/to/your/tesseract'
  ```

**Issue: Low OCR confidence scores**
- Solution: Improve image quality, increase contrast, or use `--debug` to inspect preprocessed images

**Issue: Translation model download is slow**
- Solution: First run downloads models (can be several GB). Subsequent runs use cached models.

**Issue: Parser fails to find all fields**
- Solution: Check that the plaque follows a standard format. You may need to adjust parsing logic in `parser.py`

## Future Enhancements

- [ ] Implement audio output using text-to-speech
- [ ] Add support for more languages
- [ ] Improve parser robustness with machine learning
- [ ] Add batch processing for multiple images
- [ ] Create web interface
- [ ] Add image quality validation
- [ ] Support for non-standard plaque formats

## License

This project is for educational and accessibility purposes. Please ensure you have permission to photograph and translate museum plaques before use.

## Contact

For questions or contributions, please contact Magnus Miller.
