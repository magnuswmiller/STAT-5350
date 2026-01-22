'''
translation.py

Description:
    This file handles the translation of the raw description plaque text extracted using OCR into the target
    language specified by the user.

Author:
    Magnus Miller

Date Last Updated:
    01/20/2026
'''

# Importing Libraries
from typing import Union, Tuple
from transformers import pipeline
import warnings
import torch

# Suppress warnings for cleaner CLI
warnings.filterwarnings("ignore", category=UserWarning)

# Load translator pipeline for faster runtime
_translator = None

def get_trans_pipe(source_lang: str,
                   target_lang: str,
                   model: str
                   ):
    global _translator

    if _translator is None:
        try:
            print(f"* Loading translation model: {model}.")
            _translator = pipeline("translation", model=model, tokenizer=model, device=0 if torch.cuda.is_available() else -1)
        except Exception as e:
            print(f"Model {model} not found or failed to load: {e}")
            print("Falling back to multilingual NLLB-distilled (slower but broader support)")
            _translator = pipeline("translation", model="facebook/nllb-200-distilled-600M", tokenizer="facebook/nllb-200-distilled-600M")
    return _translator

def translate(raw_text: str,
              source_lang: str = "en",
              target_lang: str = "fr",
              max_len: int = 512
              ) -> str:
    # Define Model to translate using
    print("* Defining translation model.")
    model = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"

    # Check text input
    if not raw_text.strip():
        print("* No text passed to translate.")
        return ""

    # Build translator
    print("* Building translator.")
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
        result = translator(raw_text, max_length=max_len, forced_bos_token_id=translator.tokenizer.lang_code_to_id(tgt_lang_token))
    else:
        print("* Translating text.")
        result = translator(raw_text, max_len)

    # Clean output
    print("* Cleaning translated ouput.")
    trans_text = result[0]["translation_text"].strip()

    return trans_text