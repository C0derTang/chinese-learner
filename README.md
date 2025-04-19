# Chinese Character Analysis Tool

This is an interactive tool for analyzing Chinese characters, providing features like pinyin generation, character meanings, OCR (Optical Character Recognition), and flashcards for learning.

## Features

- Text Analysis
  - Character-by-character breakdown with pinyin and meanings
  - Compound word detection
  - Full pinyin generation for sentences
- Image Processing
  - OCR support for Chinese text in images
- Flashcard System
  - Interactive flashcards for character learning
  - Shuffle and navigation controls
  - Progress tracking
- Multiple View Options
  - Full Pinyin View
  - Character List View (table format)
  - Detailed View with compound words

## Prerequisites

- Python 3.6 or higher
- Tesseract OCR (required for image processing)
  - Windows: Download and install from [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Linux: `sudo apt-get install tesseract-ocr`
  - Mac: `brew install tesseract`

## Installation

1. Clone this repository or download the source code

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Download the CC-CEDICT dictionary file:
   - Download `cedict_ts.u8` from [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cc-cedict)
   - Place the file in the same directory as the application

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. The application will open in your default web browser with two main tabs:

### Text Analysis Tab
- Enter Chinese text directly or upload an image containing Chinese text
- Click "Process Text" to analyze
- View results in three formats:
  - Full Pinyin: Shows complete pinyin for the entire text
  - Character List: Table view of characters with pinyin and meanings
  - Details View: Expandable sections showing meanings and compound words

### Flashcards Tab
- Practice with Chinese characters
- Navigate through cards using Previous/Next buttons
- Shuffle cards for randomized practice
- Toggle answers to check meanings and compounds
- Track progress with the progress bar

## File Structure

- `app.py`: Main Streamlit application
- `processor.py`: Text processing and dictionary handling
- `requirements.txt`: Python dependencies
- `chars.json`: Generated file storing character data
- `cedict_ts.u8`: Chinese-English dictionary file (must be downloaded separately)

## Notes

- For OCR functionality, ensure Tesseract is properly installed and configured
- The application requires an internet connection for Streamlit to run
- First-time processing of text may take a moment as it builds the character database 