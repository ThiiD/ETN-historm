import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO


def SingleHISTORM():
    st.set_page_config(
        page_title="Single HISTORM Temperature Data",
        page_icon=":bar_chart:",
        layout="centered",
    )
    st.title("Single HISTORM Temperature Data (62, 72, 82)")

    # Create a dropdown menu and store the selected option in a variable
    option = st.selectbox("Choose an option", ("62", "72", "82"))

    file = st.file_uploader(f"Upload xlsx file with HI{option} data", type=["xlsx"])

    if file:
        df = pd.read_excel(file)
        df = df.loc[
            (df[f"Holtec/Casks/HI{option}/Average Temp"] > 0)
            & (df[f"Holtec/Casks/HI{option}/Average Temp"] < 200)
            & (df["Holtec/Environment/TIA/Value"] > 0)
            & (df["Holtec/Environment/TIA/Value"] < 200)
            & (df[f"Holtec/Casks/HI{option}/Delta Temp"] < 200)
            & (df[f"Holtec/Casks/HI{option}/Delta Temp"] > 0)
        ]

        # Let the user select the minimum value
        min_val = st.number_input(
            "Mininum Environment Temperature (°C)",
            value=df["Holtec/Environment/TIA/Value"].min(),
        )
        # Let the user select the maximum value
        max_val = st.number_input(
            "Maximum Environment Temperature (°C)",
            value=df["Holtec/Environment/TIA/Value"].max(),
        )
        df = df[
            (df["Holtec/Environment/TIA/Value"] >= min_val)
            & (df["Holtec/Environment/TIA/Value"] <= max_val)
        ]  # Filter DataFrame
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
        # Set y-axis limits and title
        fig.update_yaxes(range=[0, 100], title_text="Temperature (°C)")
        fig.update_xaxes(title_text="Date - Time")  # Set x-axis title
        st.plotly_chart(fig)

        # Create a BytesIO object and write the DataFrame to it using ExcelWriter
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)  # Go to the start of the BytesIO object

        # Create a download button for the Excel file
        st.download_button(
            label="Download data as Excel",
            data=output,
            file_name=f"HI{option} - Environment ({min_val}, {max_val}).xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


SingleHISTORM()
