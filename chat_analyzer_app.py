import pandas as pd
import kivy 
from kivy.app import App
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from PIL import Image

def show_popup(message):
    """Display a popup with a given message."""
    popup = Popup(
        title="Analysis Result",
        content=Label(text=message),
        size_hint=(0.8, 0.4)
    )
    popup.open()

def analyze_image(file_path):
    """Perform your custom analysis on the selected image."""
    try:
        with Image.open(file_path) as img:
            text_message = pd.DataFrame(img.getdata()).to_csv("image_data.csv", index=False)
            # Perform your analysis here
            # return a summary of the text message
            text_message = text_message.split("\n")
            text_message = [line for line in text_message if line.strip() != ""]
            text_message = [line.split(",") for line in text_message]
            text_message = [line[0] for line in text_message]
            
    except FileNotFoundError:
        return "File not found! Please select a valid image file."
    except Exception as e:
        return f"Error analyzing image: {e}"

def upload_and_analyze(file_chooser):
    """Handle file upload and perform analysis."""
    selected = file_chooser.selection
    if selected:
        file_path = selected[0]
        # Call the analysis function
        analysis_result = analyze_image(file_path)
        # Display the analysis result in a popup
        show_popup(analysis_result)
    else:
        show_popup("No file selected!")

def build_ui():
    """Build the UI layout."""
    layout = BoxLayout(orientation='vertical', spacing = 20, padding = 10)

    label = Label(text="Select a image to analyze")
    layout.add_widget(label)
    #make the label bigger
    label.size_hint_y = 0.2
    label.font_size = 30
    label.color = (1, 1, 1, 1)
    label.bold = True
    label.font_name = "Roboto"

    file_chooser = FileChooserIconView()
    layout.add_widget(file_chooser)

    # Set the initial path to the current directory
    file_chooser.filters = ['*.png', '*.jpg', '*.jpeg']  # Filter for image files
    file_chooser.multiselect = False  # Allow only single file selection

    analyze_button = Button(text="Analyze", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5})
    analyze_button.bind(on_press=lambda instance: upload_and_analyze(file_chooser))
    layout.add_widget(analyze_button)

    # Make the file chooser bigger
    file_chooser.size_hint_y = 0.6
    file_chooser.size_hint_x = 1

    return layout

def navigate_back(file_chooser):
    """Navigate to the parent directory."""
    import os
    current_path = file_chooser.path
    parent_path = os.path.dirname(current_path)  # Get the parent directory
    file_chooser.path = parent_path  # Update the file chooser path

def run_app():
    """Run the Kivy app."""
    app = App()
    app.build = build_ui
    app.run()

if __name__ == "__main__":
    run_app()