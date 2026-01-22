'''
translation.py

Description:
    This file handles the translation of the raw description plaque text extracted using OCR into the target
    language specified by the user. Uses HuggingFace transformers pipeline with Helsinki-NLP models
    or falls back to NLLB multilingual models.

Author:
    Magnus Miller

Date Last Updated:
    01/22/26
'''

# Importing Libraries
from typing import Union, Tuple, Any
from transformers import pipeline
import warnings
import torch

# Suppress warnings for cleaner CLI
warnings.filterwarnings("ignore", category=UserWarning)

# Load translator pipeline for faster runtime
_translator = None

'''
get_trans_pipe()
Description:
    Initializes and returns a translation pipeline. Uses Helsinki-NLP opus-mt models for
    specific language pairs, or falls back to NLLB multilingual model if specific model
    is not available. Uses GPU if available, otherwise uses CPU.
Args:
    source_lang (str) - Source language code (2-letter ISO code)
    target_lang (str) - Target language code (2-letter ISO code)
    model (str) - Model identifier string for HuggingFace transformers
Return:
    Any - HuggingFace transformers pipeline object for translation
'''
def get_trans_pipe(source_lang: str,
                   target_lang: str,
                   model: str) -> Any:
    global _translator

    if _translator is None:
        try:
            print(f"\t* Loading translation model: {model}.")
            _translator = pipeline(
                "translation", 
                model=model, 
                tokenizer=model, 
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            print(f"Model {model} not found or failed to load: {e}")
            print("Falling back to multilingual NLLB-distilled (slower but broader support)")
            _translator = pipeline(
                "translation", 
                model="facebook/nllb-200-distilled-600M", 
                tokenizer="facebook/nllb-200-distilled-600M"
            )
    return _translator

'''
translate()
Description:
    Translates text from source language to target language using HuggingFace transformers.
    Automatically handles model selection and special token requirements for different model types.
Args:
    raw_text (str) - Text to be translated
    source_lang (str) - Source language code (2-letter ISO code, default: "en")
    target_lang (str) - Target language code (2-letter ISO code, default: "fr")
    max_len (int) - Maximum length for translation output in tokens (default: 512)
Return:
    str - Translated text, cleaned and stripped of whitespace. Returns empty string if
          input text is empty.
'''
def translate(raw_text: str,
              source_lang: str = "en",
              target_lang: str = "fr",
              max_len: int = 512) -> str:
    # Define Model to translate using
    print("\t* Defining translation model.")
    model = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"

    # Check text input
    if not raw_text.strip():
        print("\t* No text passed to translate.")
        return ""

    # Build translator
    print("\t* Building translator.")
    translator = get_trans_pipe(source_lang, target_lang, model)

    # Translate text
    # For NLLB models, you must specify forced_bos_token_id for target language
    if "nllb" in translator.model.config._name_or_path:
        # NLLB uses special tokens like 'eng_Latn', 'fra_Latn'
        # Map simple codes to NLLB format (very partial mapping - extend as needed)
        lang_map = {
            "en": "eng_Latn", "fr": "fra_Latn", "de": "deu_Latn",
            "es": "spa_Latn", "it": "ita_Latn", "zh": "zho_Hans"
            # Add more as your project needs
        }
        tgt_lang_token = lang_map.get(target_lang, f"{target_lang}_Latn")
        result = translator(
            raw_text, 
            max_length=max_len, 
            forced_bos_token_id=translator.tokenizer.lang_code_to_id(tgt_lang_token)
        )
    else:
        print("\t* Translating text.")
        result = translator(raw_text, max_len)

    # Clean output
    print("\t* Cleaning translated ouput.")
    trans_text: str = result[0]["translation_text"].strip()

    return trans_text