import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO


def SingleHISTORM():
    """
    Streamlit app for visualizing and analyzing temperature data for a single HISTORM unit.

    Allows the user to upload an Excel file with temperature data for a specific HISTORM unit (62, 72, or 82),
    visualize the data through a scatter plot, and download the filtered dataset based on user-defined temperature
    range.
    """
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="Single HISTORM Temperature Data",
        page_icon=":bar_chart:",
        layout="centered",
    )

    # Display the app title
    st.title("Single HISTORM Temperature Data (42, 52, 62, 72, 82, 63, 73, 83)")

    # Dropdown menu for selecting the HISTORM unit
    option = st.selectbox(
        "Choose an option",
        (
            "42",
            "52",
            "62",
            "72",
            "82",
            "63",
            "73",
            "83",
        ),
    )

    # File uploader for the Excel file containing the temperature data
    file = st.file_uploader(f"Upload xlsx file with HI{option} data", type=["xlsx"])

    if file:
        # Read the Excel file into a DataFrame
        df = pd.read_excel(file)
        # Filter the DataFrame based on temperature conditions
        df = df.loc[
            (df[f"Holtec/Casks/HI{option}/Average Temp"] > 0)
            & (df[f"Holtec/Casks/HI{option}/Average Temp"] < 200)
            & (df["Holtec/Environment/TIA/Value"] > 0)
            & (df["Holtec/Environment/TIA/Value"] < 200)
            & (df[f"Holtec/Casks/HI{option}/Delta Temp"] < 200)
            & (df[f"Holtec/Casks/HI{option}/Delta Temp"] > 0)
        ]

        # Number input for setting the minimum environment temperature
        min_val = st.number_input(
            "Mininum Environment Temperature (°C)",
            value=df["Holtec/Environment/TIA/Value"].min(),
        )
        # Number input for setting the maximum environment temperature
        max_val = st.number_input(
            "Maximum Environment Temperature (°C)",
            value=df["Holtec/Environment/TIA/Value"].max(),
        )
        # Further filter the DataFrame based on the user-defined temperature range
        df = df[
            (df["Holtec/Environment/TIA/Value"] >= min_val)
            & (df["Holtec/Environment/TIA/Value"] <= max_val)
        ]

        # Generate a scatter plot of the temperature data
        fig = px.scatter(
            df,
            x="t_stamp",
            y=[
                f"Holtec/Casks/HI{option}/Average Temp",
                "Holtec/Environment/TIA/Value",
                f"Holtec/Casks/HI{option}/Delta Temp",
            ],
            title=f"HI{option} Temperature Data",
        )
        # Update plot axes and titles
        fig.update_yaxes(range=[0, 100], title_text="Temperature (°C)")
        fig.update_xaxes(title_text="Date - Time")
        # Display the plot in the Streamlit app
        st.plotly_chart(fig)

        # Prepare the DataFrame for download
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)  # Reset the pointer to the beginning of the stream

        # Create a download button for the Excel file
        st.download_button(
            label="Download data as Excel",
            data=output,
            file_name=f"HI{option} - Environment ({min_val}, {max_val}).xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# Run the Streamlit app
SingleHISTORM()
