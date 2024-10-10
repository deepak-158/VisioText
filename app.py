import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import concurrent.futures
from deep_translator import GoogleTranslator
import pyperclip

def recognize_text(image, languages):
    """Recognize text from an image using EasyOCR."""
    reader = easyocr.Reader(languages, gpu=False)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = executor.submit(reader.readtext, image)
    return "\n".join([text[1] for text in result.result()])

def translate_text(text, dest_language):
    """Translate text to the specified destination language using Deep Translator."""
    try:
        translated_text = GoogleTranslator(source='auto', target=dest_language).translate(text)
        return translated_text
    except Exception as e:
        return "Translation failed."

def main():
    st.set_page_config(
        page_title="Image Text Extraction and Translation",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar for navigation and language selection
    st.sidebar.title("Navigation")
    pages = ["Text Recognition", "Text Translation"]
    page = st.sidebar.selectbox("Select a page:", pages)

    st.sidebar.title("Options")
    languages = {
        "English": "en",
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

    selected_languages = st.sidebar.multiselect("Select Image languages:", list(languages.keys()))
    default_language = st.sidebar.selectbox("Select a default Image language:", list(languages.keys()))
    translation_language = st.sidebar.selectbox("Select translation language:", list(languages.keys()))

    st.sidebar.markdown("---")
    st.sidebar.title("About the Creator")
    st.sidebar.info(
        """
        **Creator:** Deepak Shukla  
        **Contact:** [dipakshukla158@gmail.com](mailto:your.email@example.com)  
        **GitHub:** [https://github.com/deepak-158](https://github.com/YourGitHub)  
        **LinkedIn:** [www.linkedin.com/in/deepak-shukla-27a60628a](https://www.linkedin.com/in/YourLinkedIn)
        """
    )

    if page == "Text Recognition":
        st.title("Text Recognition")
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image is not None:
            # Display the uploaded image
            image = Image.open(uploaded_image)
            st.image(image, caption='Uploaded Image', use_column_width=True)

            # Convert the image to a format suitable for EasyOCR
            image_np = np.array(image)

            # Recognize text
            if selected_languages:
                extracted_text = recognize_text(image_np, [languages[lang] for lang in selected_languages])
            else:
                extracted_text = recognize_text(image_np, [languages[default_language]])
            st.subheader("Extracted Text:")
            st.write(extracted_text)
            if st.button("Copy Extracted Text"):
                pyperclip.copy(extracted_text)
                st.write("Copied to clipboard!")

    elif page == "Text Translation":
        st.title("Text Translation")
        translation_options = ["Enter text to translate", "Upload an image to translate"]
        translation_option = st.selectbox("Select a translation option:", translation_options)

        if translation_option == "Enter text to translate":
            input_text = st.text_area("Enter text to translate:")
            translate_button = st.button("Translate")
            if input_text:
                if translate_button:
                    translated_text = translate_text(input_text, languages[translation_language])
                    st.subheader("Translated Text:")
                    st.write(translated_text)
                    if st.button("Copy Translated Text"):
                        pyperclip.copy(translated_text)
                        st.write("Copied to clipboard!")

        elif translation_option == "Upload an image to translate":
            uploaded_image = st.file_uploader("Upload an image to translate", type=["jpg", "jpeg", "png"])
            if uploaded_image is not None:
                # Display the uploaded image
                image = Image.open(uploaded_image)
                st.image(image, caption='Uploaded Image', use_column_width=True)

                # Convert the image to a format suitable for EasyOCR
                image_np = np.array(image)

                # Recognize text
                if selected_languages:
                    extracted_text = recognize_text(image_np, [languages[lang] for lang in selected_languages])
                else:
                    extracted_text = recognize_text(image_np, [languages [default_language]])

                # Translate text
                translated_text = translate_text(extracted_text, languages[translation_language])
                st.subheader("Translated Text:")
                st.write(translated_text)
                if st.button("Copy Translated Text"):
                    pyperclip.copy(translated_text)
                    st.write("Copied to clipboard!")

if __name__ == "__main__":
    main()