import streamlit as st
import shutil
import os
from plot_all import plot_all
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def app():
    """
    Streamlit app for processing HISTORMs temperature data.

    This app allows users to upload an Excel file with temperature data, generates temperature plots for each HISTORM,
    packages the plots into a zip file for download, and creates a Word document with the plots embedded. The document
    and zip file are then made available for download. The app also cleans up generated files after the session.
    """
    # Configure Streamlit page settings
    st.set_page_config(
        page_title="HISTORMs Temperature Data",
        page_icon=":bar_chart:",
        layout="centered",
    )

    # Display the app title
    st.title("HISTORMs Temperature Data")

    # File uploader for the Excel file
    file = st.file_uploader("Upload xlsx file with all casks data", type=["xlsx"])

    if file:
        # Generate plots from the uploaded file and get the month and year from the data
        month_year = plot_all(file)

        # Create a zip file of the "plots" directory
        shutil.make_archive("plots", "zip", "plots")

        # Check if the zip file exists (i.e., the "plots" directory is not empty)
        if os.path.exists("plots.zip"):
            # Create a download button for the zip file
            with open("plots.zip", "rb") as f:
                bytes = f.read()
                st.download_button(
                    label="Download Temperature Plots Zip File",
                    data=bytes,
                    file_name=f"HS {month_year} Temperature Plots.zip",
                    mime="application/zip",
                )

        # List of months in Portuguese
        MESES = [
            "JANEIRO",
            "FEVEREIRO",
            "MARÇO",
            "ABRIL",
            "MAIO",
            "JUNHO",
            "JULHO",
            "AGOSTO",
            "SETEMBRO",
            "OUTUBRO",
            "NOVEMBRO",
            "DEZEMBRO",
        ]

        # Open the Word document template
        doc = Document("2PVT-UAS 06.docx")

        # Replace placeholders in the document with actual values
        for paragraph in doc.paragraphs:
            if "MMMM/YYYY" in paragraph.text:
                paragraph.text = paragraph.text.replace("MMMM/YYYY", month_year)
            if "YYYY" in paragraph.text:
                paragraph.text = paragraph.text.replace(
                    "YYYY", month_year.split(".")[1]
                )

        # Get the current directory
        current_dir = os.path.dirname(os.path.realpath(__file__))

        # Construct the path to the 'plots' directory
        plots_dir = os.path.join(current_dir, "plots")

        # List all the image files in the 'plots' directory
        files_plot = os.listdir(plots_dir)
        image_files = [
            f
            for f in files_plot
            if f.endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))
        ]

        # Add each image to the Word document
        for image_file in image_files:
            paragraph = doc.add_paragraph()
            run = paragraph.add_run()
            image_path = os.path.join(plots_dir, image_file)
            run.add_picture(image_path, width=Inches(6.70))
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT

        # Save the modified document
        doc_file_name = f"COI-DDD.O-0XX-23 - 2PVT-UAS 06 {month_year}.docx"
        doc.save(doc_file_name)

        # Create a download button for the Word document
        with open(doc_file_name, "rb") as f:
            bytes = f.read()
            st.download_button(
                label="Download COI 2PVT-UAS Word Document",
                data=bytes,
                file_name=doc_file_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

        # Clean up: Delete the zip file, the Word document, and the 'plots' directory
        os.remove("plots.zip")
        os.remove(doc_file_name)
        shutil.rmtree("plots")


# Run the app
app()
