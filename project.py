import base64

import streamlit as st
import requests
import sounddevice as sd
import wavio
from openai import OpenAI
from PIL import Image
from io import BytesIO

# Set your OpenAI API key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Function to record audio
def record_audio(filename, duration, fs):
    st.info("Recording audio...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    wavio.write(filename, recording, fs, sampwidth=2)
    st.success(f"Audio recorded and saved as {filename}")

# Function to generate an image from text
def generate_image_from_text(text):
    try:
        with st.spinner("Generating image..."):
            response = client.images.generate(
                model="gpt-image-1",
                prompt=text,
                size="1024x1024"
            )

        # Extract image (b64)
        image_base64 = response.data[0].b64_json

        # Convert base64 → Image
        image_data = BytesIO(base64.b64decode(image_base64))
        image = Image.open(image_data)

        # Save & display
        image_path = "generated_image.jpg"
        image.save(image_path)
        st.success("Image generated successfully!")
        st.image(image_path, caption="Generated Image", use_column_width=True)

        return image

    except Exception as e:
        st.error(f"An error occurred: {e}")

# Streamlit interface
st.title("Voice and Text to Image Generator")
st.write("Use your voice or enter text to generate an image using AI.")

# Input method
input_method = st.radio("Select input method:", ("Voice", "Text"))

if input_method == "Voice":
    if st.button("Click here to speak"):
        audio_filename = "input.wav"
        duration = 5
        fs = 44100

        record_audio(audio_filename, duration, fs)

        with st.spinner("Transcribing audio..."):
            audio_file = open(audio_filename, "rb")
            transcript = client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio_file
            )

        text = transcript.text
        st.write("Transcribed Text:", text)

        generate_image_from_text(text)

elif input_method == "Text":
    user_input = st.text_area("Enter your text here:")
    if st.button("Generate Image"):
        generate_image_from_text(user_input)

st.write("Powered by OpenAI")
