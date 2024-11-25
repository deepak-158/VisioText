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
        draw.rectangle([tuple(box[0]), tuple(box[2])], outline="red", width=3)  # Draw a red rectangle around the text
    return image

def text_to_speech(text):
    """Convert text to speech and play it."""
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=True) as fp:
            tts.save(f"{fp.name}.mp3")
            os.system(f"start {fp.name}.mp3")  # For Windows
            # os.system(f"afplay {fp.name}.mp3")  # For macOS
            # os.system(f"mpg321 {fp.name}.mp3")  # For Linux
    except Exception as e:
        st.error("Error in text-to-speech: " + str(e))

def main():
    st.set_page_config(
        page_title="Image Text Extraction, Translation, and Grammar Check",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar for navigation
    st.sidebar.title("****VisioText****")
    st.sidebar.subheader("Where Images Meet Text")
    pages = ["Text Recognition", "Text Translation", "Grammar Check"]
    page = st.sidebar.selectbox("Options:", pages)

    languages = {
        "English": "en",
        "Hindi": "hi",  # Added Hindi
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
    **TEAM NUMBER :** 98
    \n**TEAM MEMBERS**
    \nJiya Kathuria (23BCE11153)
    \nArnav Majithia (23BCE11196)
    \nDeepak Shukla (23BCE11422)  
    \nDevya Saigal (23BCE10961)
    \nKousumi Mondal (23BCE11147)
    """
                    )

    if page == "Text Recognition":
        st.title("Text Recognition")
        capture_option = st.selectbox("Select an option:", ["Upload an image", "Take a photo"])
        if capture_option == "Upload an image":
            uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
            if uploaded_image is not None:
                try:
                    image = Image.open(uploaded_image)
                    st.image(image, caption='Uploaded Image', use_column_width=True)

                    # Recognize text
                    results = recognize_text(np.array(image))

                    extracted_text = "\n".join([text[1] for text in results])
                    st.subheader("Extracted Text:")
                    st.write(extracted_text)

                    # Highlight text in the image
                    highlighted_image = draw_boxes_on_image(image.copy(), results)
                    st.image(highlighted_image, caption="Highlighted Text", use_column_width=True)

                    if st.button("Copy Extracted Text"):
                        pyperclip.copy(extracted_text)
                        st.write("Copied to clipboard!")

                    if st.button("Read Extracted Text"):
                        text_to_speech(extracted_text)

                except Exception as e:
                    st.error("Error processing image: " + str(e))

        elif capture_option == "Take a photo":
            image = st.camera_input("Take a photo")
            if image is not None:
                try:
                    image = Image.open(image)

                    # Recognize text
                    results = recognize_text(np.array(image))

                    extracted_text = "\n".join([text[1] for text in results])
                    st.subheader("Extracted Text:")
                    st.write(extracted_text)

                    # Highlight text in the image
                    highlighted_image = draw_boxes_on_image(image.copy(), results)
                    st.image(highlighted_image, caption="Highlighted Text", use_column_width=True)

                    if st.button("Copy Extracted Text"):
                        pyperclip.copy(extracted_text)
                        st.write("Copied to clipboard!")

                    if st.button("Read Extracted Text"):
                        text_to_speech(extracted_text)

                except Exception as e:
                    st.error("Error processing image: " + str(e))

    elif page == "Text Translation":
        st.title("Text Translation")
        translation_options = ["Enter text to translate", "Upload an image to translate", "Take a photo to translate"]
        translation_option = st.selectbox("Select a translation option:", translation_options)

        if translation_option == "Enter text to translate":
            input_text = st.text_area("Enter text to translate:")
            if input_text:
                try:
                    detected_language = detect_language(input_text)

                    st.subheader("Detected Language:")
                    st.write(detected_language)

                    translate_button = st.button("Translate")
                    if translate_button:
                        translated_text = translate_text(input_text, languages[translation_language])

                        st.subheader("Translated Text:")
                        st.write(translated_text)
                        if st.button("Copy Translated Text"):
                            pyperclip.copy(translated_text)
                            st.write("Copied to clipboard!")

                        if st.button("Read Translated Text"):
                            text_to_speech(translated_text)

                except Exception as e:
                    st.error("Error translating text: " + str(e))

        elif translation_option == "Upload an image to translate":
            uploaded_image = st.file_uploader("Upload an image to translate", type=["jpg", "jpeg", "png"])
            if uploaded_image is not None:
                try:
                    image = Image.open(uploaded_image)
                    st.image(image, caption='Uploaded Image', use_column_width=True)

                    # Recognize text
                    results = recognize_text(np.array(image))

                    extracted_text = "\n".join([text[1] for text in results])
                    st.subheader("Extracted Text:")
                    st.write(extracted_text)

                    # Highlight text in the image
                    highlighted_image = draw_boxes_on_image(image.copy(), results)
                    st.image(highlighted_image, caption="Highlighted Text", use_column_width=True)

                    # Translate text
                    translated_text = translate_text(extracted_text, languages[translation_language])

                    st.subheader("Translated Text:")
                    st.write(translated_text)
                    if st.button("Copy Translated Text"):
                        pyperclip.copy(translated_text)
                        st.write("Copied to clipboard!")

                    if st.button("Read Translated Text"):
                        text_to_speech(translated_text)

                except Exception as e:
                    st.error("Error translating image: " + str(e))

        elif translation_option == "Take a photo to translate":
            image = st.camera_input("Take a photo to translate")
            if image is not None:
                try:
                    image = Image.open(image)

                    # Recognize text
                    results = recognize_text(np.array(image))

                    extracted_text = "\n".join([text[1] for text in results])
                    st.subheader("Extracted Text:")
                    st.write(extracted_text)

                    # Highlight text in the image
                    highlighted_image = draw_boxes_on_image(image.copy(), results)
                    st.image(highlighted_image, caption="Highlighted Text", use_column_width=True)

                    # Translate text
                    translated_text = translate_text(extracted_text, languages[translation_language])

                    st.subheader("Translated Text:")
                    st.write(translated_text)
                    if st.button("Copy Translated Text"):
                        pyperclip.copy(translated_text)
                        st.write("Copied to clipboard!")

                    if st.button("Read Translated Text"):
                        text_to_speech(translated_text)

                except Exception as e:
                    st.error("Error translating image: " + str(e))

    elif page == "Grammar Check":
        st.title("Check For The Grammar")

        # Text input area for grammar check
        input_text = st.text_area("Enter text to check grammar, spelling, and punctuation:")

        if input_text:
            try:
                corrected_text, matches = check_grammar(input_text)

                st.subheader("Corrected Text:")
                st.write(corrected_text)

                if st.button("Copy Corrected Text"):
                    pyperclip.copy(corrected_text)
                    st.write("Copied to clipboard!")

                if st.button("Read Corrected Text"):
                    text_to_speech(corrected_text)

                if matches:
                    st.subheader("Grammar Issues Detected:")
                    for match in matches:
                        st.write(f"Issue: {match.message}")
                        st.write(f"Correction Suggestion: {match.replacements}")
                        st.write(f"Context: {match.context}")

            except Exception as e:
                st.error("Error checking grammar: " + str(e))


if __name__ == '__main__':
    main()