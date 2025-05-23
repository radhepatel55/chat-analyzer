import pandas as pd
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from PIL import Image
import os
import fitz  # PyMuPDF for PDFs
import pytesseract
from docx import Document
import nltk
from nltk.corpus import stopwords
from collections import Counter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


nltk.download('punkt_tab')
nltk.download('punkt')
nltk.download('stopwords')


# -----------------------------
# Popup Helper
# -----------------------------
def show_popup(message):
    # Create a ScrollView to handle long content
    scroll_view = ScrollView(size_hint=(1, None), size=(400, 400))
    
    # Add the message inside a Label
    content_label = Label(
        text=message,
        size_hint_y=None,
        text_size=(400, None),  # Wrap text within the width of the ScrollView
        halign="left",
        valign="top",
    )
    content_label.bind(texture_size=content_label.setter('size'))  # Adjust height dynamically
    scroll_view.add_widget(content_label)

    # Create a popup with the ScrollView
    popup = Popup(
        title="Analysis Result",
        content=scroll_view,
        size_hint=(0.9, 0.9),  # Adjust popup size to fit the screen
        auto_dismiss=True
    )
    popup.open()

# -----------------------------
# Text Extraction
# -----------------------------
def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".pdf":
        text = ""
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        return text
    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)
    else:
        return ""

# -----------------------------
# Text Analysis
# -----------------------------
def analyze_text(text):
    words = nltk.word_tokenize(text)
    words_clean = [w.lower() for w in words if w.isalpha()]
    stop_words = set(stopwords.words('english'))
    filtered = [w for w in words_clean if w not in stop_words]

    word_count = len(words_clean)
    char_count = len(text)
    reading_time = round(word_count / 200, 2)
    top_words = Counter(filtered).most_common(5)

    return {
        "Word Count": word_count,
        "Character Count": char_count,
        "Estimated Reading Time (min)": reading_time,
        "Top Words": ", ".join(f"{word} ({count})" for word, count in top_words)
    }

# -----------------------------
# Summarization
# -----------------------------
def summarize_text(text, sentence_count=3):
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentence_count)
        return " ".join(str(sentence) for sentence in summary)
    except Exception as e:
        return f"Could not generate summary. ({e})"

# -----------------------------
# File Processing
# -----------------------------
def analyze_file(file_path):
    try:
        text = extract_text(file_path)
        if not text.strip():
            return "No readable text found in the file."

        analysis = analyze_text(text)
        summary = summarize_text(text)

        result = (
            f"Document Analysis:\n"
            f"- Word Count: {analysis['Word Count']}\n"
            f"- Character Count: {analysis['Character Count']}\n"
            f"- Reading Time: {analysis['Estimated Reading Time (min)']} mins\n"
            f"- Top Words: {analysis['Top Words']}\n\n"
            f"Summary:\n{summary}"
        )
        return result
    except Exception as e:
        return f"Error analyzing file: {e}"

# -----------------------------
# Kivy UI
# -----------------------------
def upload_and_analyze(file_chooser):
    selected = file_chooser.selection
    if selected:
        file_path = selected[0]
        result = analyze_file(file_path)
        show_popup(result)
    else:
        show_popup("No file selected!")

def build_ui():
    layout = BoxLayout(orientation='vertical', spacing=20, padding=10)

    # Center the label text
    label = Label(
        text="Select a document or image to analyze",
        size_hint_y=0.2,
        font_size=24,
        color=(1, 1, 1, 1),
        bold=True,
        halign="center",  # Horizontal alignment
        valign="middle",  # Vertical alignment
        text_size=(None, None)  # Ensure text wraps properly
    )
    label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))  # Dynamically adjust text size
    layout.add_widget(label)

    file_chooser = FileChooserIconView()
    file_chooser.filters = ['*.png', '*.jpg', '*.jpeg', '*.txt', '*.pdf', '*.docx']
    file_chooser.multiselect = False
    file_chooser.size_hint_y = 0.6
    layout.add_widget(file_chooser)

    analyze_button = Button(text="Analyze", size_hint=(0.3, 0.1), pos_hint={'center_x': 0.5})
    analyze_button.bind(on_press=lambda instance: upload_and_analyze(file_chooser))
    layout.add_widget(analyze_button)

    return layout

def run_app():
    app = App()
    app.build = build_ui
    app.run()


if __name__ == "__main__":
    run_app()