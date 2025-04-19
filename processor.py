import json
import os
from typing import Dict, List, Optional, Tuple
from pypinyin import pinyin, Style

def load_chars_json() -> Dict:
    """Load existing characters from chars.json"""
    if os.path.exists('chars.json') and os.path.getsize('chars.json') > 0:
        with open('chars.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_chars_json(chars_dict: Dict) -> None:
    """Save characters to chars.json"""
    with open('chars.json', 'w', encoding='utf-8') as f:
        json.dump(chars_dict, f, ensure_ascii=False, indent=2)

def get_pinyin(char: str) -> str:
    """Get pinyin for a character"""
    result = pinyin(char, style=Style.TONE)[0][0]
    return result

def process_text_file(filename: str) -> str:
    """Read and process a text file, return its content"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def find_compound_words(text: str) -> Dict[str, List[str]]:
    """Find compound words for each character from cedict_ts.u8"""
    char_compounds = {}
    
    try:
        with open('cedict_ts.u8', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                    
                parts = line.strip().split('/')
                if not parts:
                    continue
                    
                # Get the simplified character(s) from the line
                simplified = parts[0].split()[1] if len(parts[0].split()) > 1 else ''
                
                # Skip single characters in dictionary (we'll handle those separately)
                if len(simplified) < 2:
                    continue
                
                # If this compound appears in our text
                if simplified in text:
                    # Add this compound to each character's compound list
                    for char in simplified:
                        if char not in char_compounds:
                            char_compounds[char] = []
                        if simplified not in char_compounds[char]:
                            char_compounds[char].append(simplified)
    
    except FileNotFoundError:
        print("Warning: cedict_ts.u8 not found")
    
    return char_compounds

def get_meaning_from_cedict(char: str, compounds: List[str] = None) -> Tuple[str, List[str]]:
    """Get the meaning of a character and its compounds from cedict_ts.u8"""
    meanings = []
    compound_meanings = []
    
    try:
        with open('cedict_ts.u8', 'r', encoding='utf-8') as f:
            # First pass: find single character meaning
            for line in f:
                if line.startswith('#'):
                    continue
                parts = line.strip().split('/')
                if not parts:
                    continue
                
                entry_parts = parts[0].split()
                if len(entry_parts) > 1:
                    simplified = entry_parts[1]
                    if simplified == char:
                        meanings.extend([m for m in parts[1:-1] if m])
                        break
            
            # Second pass: find compound meanings if any
            if compounds:
                f.seek(0)
                for line in f:
                    if line.startswith('#'):
                        continue
                    parts = line.strip().split('/')
                    if not parts:
                        continue
                    
                    entry_parts = parts[0].split()
                    if len(entry_parts) > 1:
                        simplified = entry_parts[1]
                        if simplified in compounds:
                            compound_meanings.append({
                                'word': simplified,
                                'meaning': '; '.join([m for m in parts[1:-1] if m])
                            })
    
    except FileNotFoundError:
        print("Warning: cedict_ts.u8 not found")
    
    meaning = '; '.join(meanings) if meanings else "Meaning not found in CEDICT"
    return meaning, compound_meanings

def process_chinese_text(text: str) -> None:
    """Process Chinese text and update chars.json"""
    chars_dict = load_chars_json()
    
    # First find all compound words in the text
    compounds_dict = find_compound_words(text)
    
    # Process each unique character
    for char in set(text):
        if not '\u4e00' <= char <= '\u9fff':  # Skip non-Chinese characters
            continue
            
        if char not in chars_dict:
            char_pinyin = get_pinyin(char)
            compounds = compounds_dict.get(char, [])
            meaning, compound_meanings = get_meaning_from_cedict(char, compounds)
            
            # Create new entry
            chars_dict[char] = {
                "pinyin": char_pinyin,
                "meaning": meaning,
                "compounds": compound_meanings
            }
    
    # Save updated dictionary
    save_chars_json(chars_dict)

def main():
    input_file = "input.txt"
    
    try:
        text = process_text_file(input_file)
        process_chinese_text(text)
        print("Processing completed successfully!")
    except FileNotFoundError:
        print(f"Error: {input_file} not found. Please create it with Chinese text.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
