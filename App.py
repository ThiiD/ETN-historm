import streamlit as st
import shutil
import os
from plot_all import plot_all
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def app():
    st.title('HS Temperature Data')
    file = st.file_uploader('Upload a file', type=['xlsx'])

    if file:
        month_year = plot_all(file)

        # Create a zip file of the "plots" directory
        shutil.make_archive('plots', 'zip', 'plots')

        # Check if the zip file exists (i.e., the "plots" directory is not empty)
        if os.path.exists('plots.zip'):
            # Create a download button for the zip file
            with open('plots.zip', 'rb') as f:
                bytes = f.read()
                st.download_button(
                    label="Download plots",
                    data=bytes,
                    # Use the formatted date string
                    file_name=f"HS {month_year} Temperature Plots.zip",
                    mime="application/zip"
                )

        MESES = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO',
                 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']

        # Open the document
        doc = Document('2PVT-UAS 06.docx')

        # Replace 'YYYY' with `month_year` in all paragraphs
        for paragraph in doc.paragraphs:
            if 'MMMM/YYYY' in paragraph.text:
                paragraph.text = paragraph.text.replace('MMMM/YYYY', month_year)
            if 'YYYY' in paragraph.text:
                paragraph.text = paragraph.text.replace('YYYY', month_year.split('.')[1])

        # Get the current directory
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Construct the path to the 'plots' directory
        plots_dir = os.path.join(current_dir, 'plots')

        # List all the images in the 'plots' directory
        files_plot = os.listdir(plots_dir)
        image_files = [f for f in files_plot if f.endswith(
            ('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        # Add each image to the document
        for image_file in image_files:
            # Create a new paragraph
            paragraph = doc.add_paragraph()

            # Add an image to the paragraph
            run = paragraph.add_run()
            # Construct the full path to the image file
            image_path = os.path.join(plots_dir, image_file)
            run.add_picture(image_path, width=Inches(6.70))

            # Align the paragraph to the right
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

        # Save the document
        doc_file_name = f'COI-DDD.O-0XX-23 - 2PVT-UAS 06 {month_year}.docx'
        doc.save(doc_file_name)

        # Create a download button for the docx file
        with open(doc_file_name, 'rb') as f:
            bytes = f.read()
            st.download_button(
                label="Download docx",
                data=bytes,
                file_name=doc_file_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        # Delete the zip file and the 'plots' directory
        os.remove('plots.zip')
        os.remove(doc_file_name)
        shutil.rmtree('plots')


app()
