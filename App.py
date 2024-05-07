import streamlit as st
import shutil
import os
from plot_all import plot_all
from datetime import datetime  # Add this line


def app():
    st.title('HISTORMs Temperature Data')
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
                    file_name=f"HISTORM {month_year} Temperature Plots.zip",
                    mime="application/zip"
                )


app()
