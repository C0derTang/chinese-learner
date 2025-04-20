import streamlit as st
import json
from processor import process_chinese_text, load_chars_json
from pypinyin import pinyin, Style
from PIL import Image
import pytesseract
import random
from character_lists import (
    load_character_lists, add_to_list, remove_from_list,
    create_list, delete_list, get_characters_in_list, get_all_lists
)

# Configure pytesseract to use the installed Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def get_full_pinyin(text: str) -> str:
    # Get pinyin with tone marks
    result = pinyin(text, style=Style.TONE)
    # Flatten the list and join with spaces
    return ' '.join([item[0] for item in result])

def extract_text_from_image(image):
    try:
        # Use pytesseract to do OCR on the image
        text = pytesseract.image_to_string(image, lang='chi_sim')
        return text.strip()
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return ""

def initialize_flashcard_state():
    if 'current_char_index' not in st.session_state:
        st.session_state.current_char_index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False
    if 'flashcard_chars' not in st.session_state:
        # Load all characters from JSON at initialization
        chars_dict = load_chars_json()
        st.session_state.flashcard_chars = [(char, info) for char, info in chars_dict.items()]
        random.shuffle(st.session_state.flashcard_chars)  # Shuffle initially
    if 'selected_list' not in st.session_state:
        st.session_state.selected_list = "All Characters"
    if 'new_list_name' not in st.session_state:
        st.session_state.new_list_name = ""

def filter_flashcards_by_list(list_name: str):
    """Filter flashcards based on selected list"""
    chars_dict = load_chars_json()
    if list_name == "All Characters":
        st.session_state.flashcard_chars = [(char, info) for char, info in chars_dict.items()]
    else:
        char_set = get_characters_in_list(list_name)
        st.session_state.flashcard_chars = [(char, info) for char, info in chars_dict.items() if char in char_set]
    if st.session_state.flashcard_chars:
        random.shuffle(st.session_state.flashcard_chars)
        st.session_state.current_char_index = 0
        st.session_state.show_answer = False

def next_flashcard():
    st.session_state.current_char_index = (st.session_state.current_char_index + 1) % len(st.session_state.flashcard_chars)
    st.session_state.show_answer = False

def previous_flashcard():
    st.session_state.current_char_index = (st.session_state.current_char_index - 1) % len(st.session_state.flashcard_chars)
    st.session_state.show_answer = False

def toggle_answer():
    st.session_state.show_answer = not st.session_state.show_answer

def shuffle_flashcards():
    random.shuffle(st.session_state.flashcard_chars)
    st.session_state.current_char_index = 0
    st.session_state.show_answer = False

def main():
    st.title("Chinese Character Analysis Tool")
    st.write("Enter Chinese text to analyze characters and find their meanings, pinyin, and compound words.")

    # Initialize session state for flashcards
    initialize_flashcard_state()

    # Create tabs for different sections
    main_tab1, main_tab2, main_tab3 = st.tabs(["Text Analysis", "Flashcards", "Character Lists"])

    with main_tab1:
        # Create tabs for input methods
        input_tab1, input_tab2 = st.tabs(["Text Input", "Image Upload"])

        with input_tab1:
            # Text input area
            text_input = st.text_area("Enter Chinese text:", height=150)
            process_button = st.button("Process Text")
            
        with input_tab2:
            uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_column_width=True)
                if st.button("Extract Text from Image"):
                    text_input = extract_text_from_image(image)
                    st.write("Extracted text:")
                    st.write(text_input)
                    process_button = True

        if process_button and text_input and text_input.strip():
            # Process the text
            process_chinese_text(text_input)
            
            # Load and display results
            chars_dict = load_chars_json()
            
            st.subheader("Analysis Results")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Full Pinyin", "Character List", "Details View"])
            
            with tab1:
                # Show complete pinyin for the entire text
                st.subheader("Complete Pinyin")
                st.write("Original text:")
                st.write(text_input)
                st.write("Pinyin:")
                full_pinyin = get_full_pinyin(text_input)
                st.write(full_pinyin)
            
            with tab2:
                # Display as a table
                data = []
                for char, info in chars_dict.items():
                    if char in text_input:  # Only show characters from input
                        data.append({
                            "Character": char,
                            "Pinyin": info["pinyin"],
                            "Meaning": info["meaning"]
                        })
                if data:
                    st.dataframe(data)
                else:
                    st.info("No Chinese characters found in the input text.")
            
            with tab3:
                # Detailed view with compounds
                for char in text_input:
                    if char in chars_dict and '\u4e00' <= char <= '\u9fff':
                        info = chars_dict[char]
                        with st.expander(f"{char} ({info['pinyin']})"):
                            st.write("**Meaning:**", info["meaning"])
                            
                            if info["compounds"]:
                                st.write("**Compound Words:**")
                                for compound in info["compounds"]:
                                    st.write(f"- {compound['word']}: {compound['meaning']}")
        elif process_button:
            st.warning("Please enter some Chinese text to process.")

    with main_tab2:
        if st.session_state.flashcard_chars:
            # Add list selection dropdown
            all_lists = ["All Characters"] + get_all_lists()
            selected_list = st.selectbox(
                "Select Character List",
                all_lists,
                index=all_lists.index(st.session_state.selected_list)
            )
            
            if selected_list != st.session_state.selected_list:
                st.session_state.selected_list = selected_list
                filter_flashcards_by_list(selected_list)

            st.write(f"Practice with characters from: {selected_list}")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.button("Previous", on_click=previous_flashcard)
            with col2:
                st.button("Shuffle Cards", on_click=shuffle_flashcards)
            with col3:
                st.button("Next", on_click=next_flashcard)

            # Display current flashcard
            current_char, current_info = st.session_state.flashcard_chars[st.session_state.current_char_index]
            
            # Create a card-like container
            card_container = st.container()
            with card_container:
                st.markdown(
                    f"""
                    <div style='padding: 20px; border-radius: 10px; border: 2px solid #f0f0f0; text-align: center;'>
                        <h1 style='font-size: 72px;'>{current_char}</h1>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Add favorite/list management buttons
            col1, col2 = st.columns(2)
            with col1:
                available_lists = get_all_lists()
                selected_list_to_add = st.selectbox("Add to list:", available_lists, key="add_to_list")
                if st.button("Add to Selected List"):
                    add_to_list(selected_list_to_add, current_char)
                    st.success(f"Added {current_char} to {selected_list_to_add}")
            
            with col2:
                if st.session_state.selected_list != "All Characters":
                    if st.button("Remove from Current List"):
                        remove_from_list(st.session_state.selected_list, current_char)
                        filter_flashcards_by_list(st.session_state.selected_list)
                        st.success(f"Removed {current_char} from {st.session_state.selected_list}")

            # Toggle answer button
            st.button("Show/Hide Answer", on_click=toggle_answer)

            # Show answer if toggled
            if st.session_state.show_answer:
                answer_container = st.container()
                with answer_container:
                    st.markdown(
                        f"""
                        <div style='padding: 20px; border-radius: 10px; border: 2px solid #f0f0f0; text-align: center;'>
                            <h3>Pinyin: {current_info['pinyin']}</h3>
                            <h3>Meaning: {current_info['meaning']}</h3>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    if current_info["compounds"]:
                        st.markdown(
                            f"""
                            <div style='padding: 20px; border-radius: 10px; border: 2px solid #e0e0e0; margin-top: 10px;'>
                                <h4 style='text-align: center;'>Common Compounds</h4>
                                <hr style='margin: 10px 0;'>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        # Create a grid layout for compounds
                        cols = st.columns(2)
                        for idx, compound in enumerate(current_info["compounds"]):
                            with cols[idx % 2]:
                                st.markdown(
                                    f"""
                                    <div style='padding: 10px; border-radius: 5px; border: 1px solid #e0e0e0; margin: 5px 0;'>
                                        <h4 style='margin: 0; color: #1f77b4;'>{compound['word']}</h4>
                                        <p style='margin: 5px 0;'>{compound['meaning']}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

            # Show progress
            total_cards = len(st.session_state.flashcard_chars)
            st.progress((st.session_state.current_char_index + 1) / total_cards)
            st.write(f"Card {st.session_state.current_char_index + 1} of {total_cards}")
        else:
            if st.session_state.selected_list == "All Characters":
                st.error("No characters loaded. Please check the characters JSON file.")
            else:
                st.warning(f"No characters in the selected list: {st.session_state.selected_list}")
    
    with main_tab3:
        st.subheader("Manage Character Lists")
        
        # Create new list
        col1, col2 = st.columns([3, 1])
        with col1:
            new_list_name = st.text_input("New list name:", key="new_list_input")
        with col2:
            if st.button("Create List") and new_list_name:
                create_list(new_list_name)
                st.success(f"Created new list: {new_list_name}")
        
        # Display existing lists
        st.subheader("Existing Lists")
        for list_name in get_all_lists():
            with st.expander(f"{list_name} ({len(get_characters_in_list(list_name))} characters)"):
                chars = get_characters_in_list(list_name)
                if chars:
                    # Display characters in a grid with remove buttons
                    for i in range(0, len(chars), 4):  # Show 4 characters per row
                        cols = st.columns(4)
                        for j, char in enumerate(sorted(chars)[i:i+4]):
                            with cols[j]:
                                # Create a container for each character
                                st.markdown(
                                    f"""
                                    <div style='text-align: center; padding: 10px; border: 1px solid #e0e0e0; border-radius: 5px;'>
                                        <h3 style='margin: 0;'>{char}</h3>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                                # Add remove button for each character
                                if st.button(f"Remove {char}", key=f"remove_{list_name}_{char}"):
                                    remove_from_list(list_name, char)
                                    st.success(f"Removed {char} from {list_name}")
                                    st.rerun()
                    
                    if list_name != "Favorites":  # Prevent deletion of Favorites list
                        st.markdown("<hr>", unsafe_allow_html=True)
                        if st.button(f"Delete List: {list_name}"):
                            delete_list(list_name)
                            st.success(f"Deleted list: {list_name}")
                            st.rerun()
                else:
                    st.info("No characters in this list yet.")

if __name__ == "__main__":
    main() 