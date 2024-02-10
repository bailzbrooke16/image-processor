from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Base folder where images are stored
BASE_IMAGE_FOLDER = 'static/images'
# Excel file where metadata is stored
EXCEL_FILE = 'metadata.xlsx'

# Ensure the Excel file exists
if not os.path.exists(EXCEL_FILE):
    pd.DataFrame(columns=['Plot Name', 'Subplot Name', 'Folder', 'Image Name', 'Date', 'Time', 'Valid', 'Number of Species', 'What Species', 'How Many Individuals']).to_excel(EXCEL_FILE, index=False)

def find_images(base_folder):
    """Recursively find all image files in the base_folder."""
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                yield os.path.join(root, file)

@app.route('/image/<path:filename>')
def custom_static(filename):
    return send_from_directory('', filename)

    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Collect metadata from the form
        metadata = {
            'Plot Name': request.form['plot_name'],
            'Subplot Name': request.form['subplot_name'],
            'Folder': request.form['folder'],
            'Image Name': request.form['image_name'],
            'Date': request.form['date'],
            'Time': request.form['time'],
            'Valid': request.form['valid'],
            'Number of Species': request.form['number_of_species'],
            'What Species': request.form['what_species'],
            'How Many Individuals': request.form['how_many_individuals']
        }
        
        # Append metadata to Excel file
        df = pd.read_excel(EXCEL_FILE)
        df = pd.concat([df, pd.DataFrame([metadata])], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        return redirect(url_for('index'))

    # Get list of image files
    image_files = list(find_images(BASE_IMAGE_FOLDER))

    # Read current metadata
    df = pd.read_excel(EXCEL_FILE)

    # Filter out images that already have metadata
    image_files = [img for img in image_files if os.path.basename(img) not in df['Image Name'].values]

    # Select the first image to display, if available
    image_to_display = image_files[0] if image_files else None
    image_folder = os.path.dirname(image_to_display) if image_to_display else None

    # Get current date and time
    now = datetime.now()
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.strftime('%H:%M:%S')

    return render_template('index.html', image_to_display=image_to_display, image_folder=image_folder, current_date=current_date, current_time=current_time)

if __name__ == '__main__':
    app.run(debug=True)
