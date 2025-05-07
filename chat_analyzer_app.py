import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
import re

# Load sentiment analyzer
sentiment_analyzer = pipeline("sentiment-analysis")

st.title("📱 Chat Screenshot Analyzer")

# Upload image
uploaded_file = st.file_uploader("Upload a chat screenshot (JPG, PNG)", type=["png", "jpg", "jpeg"])
if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Screenshot", use_column_width=True)

    # OCR
    extracted_text = pytesseract.image_to_string(image)
    st.subheader("Extracted Text")
    st.text(extracted_text)

    # Basic chat parsing (e.g., "User: message" or timestamps)
    lines = extracted_text.strip().split("\n")
    chat_data = []
    for line in lines:
        match = re.match(r"^(\w+): (.+)", line)
        if match:
            sender, message = match.groups()
            chat_data.append({"sender": sender, "message": message})

    if not chat_data:
        st.warning("Couldn't parse chat. Please ensure clear formatting (e.g., 'Name: Message').")
    else:
        df = pd.DataFrame(chat_data)
        df['sentiment'] = df['message'].apply(lambda x: sentiment_analyzer(x)[0]['label'])

        st.subheader("📊 Sentiment Overview")
        st.dataframe(df)

        # Plot sentiment distribution
        sentiment_counts = df['sentiment'].value_counts()
        st.bar_chart(sentiment_counts)

        # Speaker contribution
        speaker_counts = df['sender'].value_counts()
        st.subheader("🗣️ Speaker Contribution")
        st.pyplot(speaker_counts.plot.pie(autopct='%1.1f%%', title="Speaker Contribution").figure)

        # Conclusions
        st.subheader("🧠 Conclusions")
        conclusions = []
        if (df['sentiment'] == 'NEGATIVE').sum() > 1:
            conclusions.append("Multiple negative messages detected — possible conflict or dissatisfaction.")
        if df['sender'].value_counts().idxmax():
            dominant = df['sender'].value_counts().idxmax()
            conclusions.append(f"{dominant} spoke the most during the conversation.")
        if not conclusions:
            conclusions.append("Conversation appears neutral and balanced.")

        for c in conclusions:
            st.write("- " + c)
