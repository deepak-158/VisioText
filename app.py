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


def draw_boxes_on_image(image, results):
    """Draw bounding boxes around recognized text on the image."""
    draw = ImageDraw.Draw(image)
    for result in results:
        box = result[0]  # Coordinates of the bounding box
        draw.rectangle([tuple(box[0]), tuple(box[2])], outline="red", width=3)
    return image


def process_image(image_file):
    """Process uploaded or captured image for text recognition."""
    if image_file is not None:
        try:
            image = Image.open(image_file)
            st.image(image, caption='Image', use_column_width=True)

            results = recognize_text(np.array(image))
            if isinstance(results, str):
                st.error(f"Error recognizing text: {results}")
                return

            extracted_text = "\n".join([text[1] for text in results])
            st.subheader("Extracted Text:")
            st.write(extracted_text)

            highlighted_image = draw_boxes_on_image(image.copy(), results)
            st.image(highlighted_image, caption="Highlighted Text", use_column_width=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy Extracted Text"):
                    pyperclip.copy(extracted_text)
                    st.success("Copied to clipboard!")
            with col2:
                if st.button("Read Extracted Text"):
                    text_to_speech(extracted_text)

        except Exception as e:
            st.error(f"Error processing image: {str(e)}")


def process_text_translation(text, target_lang):
    """Process text translation."""
    try:
        detected_language = detect_language(text)
        st.subheader("Detected Language:")
        st.write(detected_language)

        if st.button("Translate"):
            translated_text = translate_text(text, target_lang)
            st.subheader("Translated Text:")
            st.write(translated_text)

            if st.button("Copy Translated Text"):
                pyperclip.copy(translated_text)
                st.success("Copied to clipboard!")

    except Exception as e:
        st.error(f"Error translating text: {str(e)}")


def process_image_translation(image_file, target_lang):
    """Process image translation."""
    if image_file is not None:
        try:
            image = Image.open(image_file)
            st.image(image, caption='Image', use_column_width=True)

            results = recognize_text(np.array(image))
            if isinstance(results, str):
                st.error(f"Error recognizing text: {results}")
                return

            extracted_text = "\n".join([text[1] for text in results])
            st.subheader("Extracted Text:")
            st.write(extracted_text)

            highlighted_image = draw_boxes_on_image(image.copy(), results)
            st.image(highlighted_image, caption="Highlighted Text", use_column_width=True)

            translated_text = translate_text(extracted_text, target_lang)
            st.subheader("Translated Text:")
            st.write(translated_text)

            if st.button("Copy Translated Text"):
                pyperclip.copy(translated_text)
                st.success("Copied to clipboard!")

        except Exception as e:
            st.error(f"Error translating image: {str(e)}")


def process_grammar_check(text):
    """Process grammar check."""
    try:
        if st.button("Check Grammar"):
            corrected_text, matches = check_grammar(text)

            # Display original text
            st.subheader("Original Text:")
            st.write(text)

            # Display corrected text
            st.subheader("Corrected Text:")
            st.write(corrected_text)

            if st.button("Copy Corrected Text"):
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