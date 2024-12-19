import streamlit as st
import language_tool_python
import easyocr
from PIL import Image, ImageDraw
import numpy as np
import langdetect
from deep_translator import GoogleTranslator
import pyperclip
from gtts import gTTS
import os
import tempfile
import base64


def autoplay_audio(file_path: str):
    """Autoplay the audio file using HTML audio element."""
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)


def text_to_speech(text, lang='en'):
    """Convert text to speech and play it in the web browser."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as fp:
            tts = gTTS(text=text, lang=lang)
            tts.save(fp.name)

            # Open and read the audio file
            with open(fp.name, 'rb') as audio_file:
                audio_bytes = audio_file.read()

            # Display audio player in Streamlit
            st.audio(audio_bytes, format='audio/mp3')

            # Clean up the temporary file
            os.unlink(fp.name)
    except Exception as e:
        st.error(f"Error in text-to-speech: {str(e)}")


def recognize_text(image):
    """Recognize text from an image using EasyOCR and return the results with bounding boxes."""
    try:
        reader = easyocr.Reader(['en'], gpu=False)
        result = reader.readtext(image)
        return result
    except Exception as e:
        return str(e)


def detect_language(text):
    """Detect the language of the text."""
    try:
        language = langdetect.detect(text)
        return language
    except langdetect.lang_detect_exception.LangDetectException:
        return "Unknown"
    except Exception as e:
        return str(e)


def translate_text(text, dest_language):
    """Translate text to the specified destination language using Deep Translator."""
    try:
        translated_text = GoogleTranslator(source='auto', target=dest_language).translate(text)
        return translated_text
    except Exception as e:
        return "Translation failed: " + str(e)


def check_grammar(text):
    """Check grammar, spelling, and punctuation using LanguageTool."""
    try:
        tool = language_tool_python.LanguageTool('en-US')
        matches = tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        return corrected_text, matches
    except Exception as e:
        return str(e), []


def draw_boxes_on_image(image, results, original_size):
    """Draw bounding boxes around recognized text on the image."""
    draw = ImageDraw.Draw(image)

    # Get current image dimensions
    current_width, current_height = image.size
    original_width, original_height = original_size

    # Calculate scaling factors
    width_scale = current_width / original_width
    height_scale = current_height / original_height

    for result in results:
        # Get coordinates from the result
        box = result[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]

        # Scale the coordinates
        scaled_box = []
        for point in box:
            scaled_x = point[0] * width_scale
            scaled_y = point[1] * height_scale
            scaled_box.append((int(scaled_x), int(scaled_y)))

        # Draw the polygon using scaled coordinates
        draw.polygon(scaled_box, outline="red", width=2)

    return image


def process_image(image_file):
    """Process uploaded or captured image for text recognition."""
    if image_file is not None:
        try:
            # Open and get original image size
            image = Image.open(image_file)
            original_size = image.size

            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)

            # Resize image for preview
            preview_width = 400  # You can adjust this value
            aspect_ratio = image.height / image.width
            preview_height = int(preview_width * aspect_ratio)
            preview_image = image.resize((preview_width, preview_height))

            # Display original image in first column
            with col1:
                st.subheader("Original Image")
                st.image(preview_image, use_column_width=True)

            # Process the original image for text recognition
            results = recognize_text(np.array(image))
            if isinstance(results, str):
                st.error(f"Error recognizing text: {results}")
                return

            extracted_text = "\n".join([text[1] for text in results])

            # Display highlighted image in second column
            highlighted_image = draw_boxes_on_image(preview_image.copy(), results, original_size)
            with col2:
                st.subheader("Detected Text")
                st.image(highlighted_image, use_column_width=True)

            # Display extracted text below the images
            st.subheader("Extracted Text:")
            st.write(extracted_text)

            # Create two columns for buttons
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Copy Extracted Text", key="copy_extracted"):
                    pyperclip.copy(extracted_text)
                    st.success("Copied to clipboard!")
            with btn_col2:
                if st.button("Read Extracted Text", key="read_extracted"):
                    text_to_speech(extracted_text)

        except Exception as e:
            st.error(f"Error processing image: {str(e)}")


def process_text_translation(text, target_lang):
    """Process text translation."""
    try:
        detected_language = detect_language(text)
        st.subheader("Detected Language:")
        st.write(detected_language)

        # Create a container for the translation results
        translation_container = st.container()

        if st.button("Translate", key="translate_text"):
            translated_text = translate_text(text, target_lang)
            with translation_container:
                st.subheader("Translated Text:")
                st.write(translated_text)

                # Create a separate button for copying
                if st.button("Copy Translated Text", key="copy_translated_text"):
                    pyperclip.copy(translated_text)
                    st.success("Copied to clipboard!")

    except Exception as e:
        st.error(f"Error translating text: {str(e)}")


def process_image_translation(image_file, target_lang):
    """Process image translation."""
    if image_file is not None:
        try:
            # Open and get original image size
            image = Image.open(image_file)
            original_size = image.size

            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)

            # Resize image for preview
            preview_width = 400  # You can adjust this value
            aspect_ratio = image.height / image.width
            preview_height = int(preview_width * aspect_ratio)
            preview_image = image.resize((preview_width, preview_height))

            # Display original image in first column
            with col1:
                st.subheader("Original Image")
                st.image(preview_image, use_column_width=True)

            # Process the original image for text recognition
            results = recognize_text(np.array(image))
            if isinstance(results, str):
                st.error(f"Error recognizing text: {results}")
                return

            extracted_text = "\n".join([text[1] for text in results])

            # Display highlighted image in second column
            highlighted_image = draw_boxes_on_image(preview_image.copy(), results, original_size)
            with col2:
                st.subheader("Detected Text")
                st.image(highlighted_image, use_column_width=True)

            # Display extracted text
            text_container = st.container()
            with text_container:
                st.subheader("Extracted Text:")
                st.write(extracted_text)
                if st.button("Copy Extracted Text", key="copy_img_extracted"):
                    pyperclip.copy(extracted_text)
                    st.success("Copied to clipboard!")

            # Display translated text
            translation_container = st.container()
            translated_text = translate_text(extracted_text, target_lang)
            with translation_container:
                st.subheader("Translated Text:")
                st.write(translated_text)
                if st.button("Copy Translated Text", key="copy_img_translated"):
                    pyperclip.copy(translated_text)
                    st.success("Copied to clipboard!")

        except Exception as e:
            st.error(f"Error translating image: {str(e)}")


def process_grammar_check(text):
    """Process grammar check."""
    try:
        # Create containers for different sections
        results_container = st.container()

        if st.button("Check Grammar", key="check_grammar"):
            corrected_text, matches = check_grammar(text)

            with results_container:
                # Display original text
                st.subheader("Original Text:")
                st.write(text)
                if st.button("Copy Original Text", key="copy_original"):
                    pyperclip.copy(text)
                    st.success("Copied to clipboard!")

                # Display corrected text
                st.subheader("Corrected Text:")
                st.write(corrected_text)
                if st.button("Copy Corrected Text", key="copy_corrected"):
                    pyperclip.copy(corrected_text)
                    st.success("Copied to clipboard!")

                # Display differences
                if text != corrected_text:
                    st.subheader("Changes Made:")
                    st.info("The following changes were made to improve the text:")
                    for match in matches:
                        with st.expander(f"Issue: {match.message}"):
                            st.write(f"Original: {match.context}")
                            st.write(f"Suggestion: {', '.join(match.replacements)}")
                            st.write(f"Rule ID: {match.ruleId}")
                else:
                    st.success("No grammar issues found in the text!")

    except Exception as e:
        st.error(f"Error checking grammar: {str(e)}")


def main():
    st.set_page_config(
        page_title="Image Text Extraction, Translation, and Grammar Check",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add custom CSS for better button styling
    st.markdown("""
        <style>
        .stButton > button {
            width: 100%;
            margin-bottom: 10px;
        }
        .stExpander {
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

    # Sidebar for navigation
    st.sidebar.title("VisioText")
    st.sidebar.subheader("Where Images Meet Text")
    pages = ["Text Recognition", "Text Translation", "Grammar Check"]
    page = st.sidebar.selectbox("Options:", pages)

    languages = {
        "English": "en",
        "Hindi": "hi",
        "French": "fr",
        "Spanish": "es",
        "German": "de",
        "Italian": "it",
        "Portuguese": "pt",
        "Dutch": "nl",
        "Russian": "ru",
        "Chinese": "zh",
        "Japanese": "ja",
        "Korean": "ko"
    }

    translation_language = st.sidebar.selectbox("Select translation language:", list(languages.keys()))
    st.sidebar.markdown("---")
    st.sidebar.title("About the Creator")
    st.sidebar.info("""
    **TEAM NUMBER:** 98
    \n**TEAM MEMBERS**
    \nJiya Kathuria (23BCE11153)
    \nArnav Majithia (23BCE11196)
    \nDeepak Shukla (23BCE11422)
    \nDevya Saigal (23BCE10961)
    \nKousumi Mondal (23BCE11147)
    """)

    if page == "Text Recognition":
        st.title("Text Recognition")
        capture_option = st.selectbox("Select an option:", ["Upload an image", "Take a photo"])

        if capture_option == "Upload an image":
            uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            process_image(uploaded_image)

        elif capture_option == "Take a photo":
            image = st.camera_input("Take a photo")
            process_image(image)

    elif page == "Text Translation":
        st.title("Text Translation")
        translation_options = ["Enter text to translate", "Upload an image to translate", "Take a photo to translate"]
        translation_option = st.selectbox("Select a translation option:", translation_options)

        if translation_option == "Enter text to translate":
            input_text = st.text_area("Enter text to translate:")
            if input_text:
                process_text_translation(input_text, languages[translation_language])

        elif translation_option == "Upload an image to translate":
            uploaded_image = st.file_uploader("Upload an image to translate", type=["jpg", "jpeg", "png"])
            process_image_translation(uploaded_image, languages[translation_language])

        elif translation_option == "Take a photo to translate":
            image = st.camera_input("Take a photo to translate")
            process_image_translation(image, languages[translation_language])

    elif page == "Grammar Check":
        st.title("Grammar Check")
        input_text = st.text_area("Enter text to check grammar, spelling, and punctuation:")
        if input_text:
            process_grammar_check(input_text)


if __name__ == '__main__':
    main()