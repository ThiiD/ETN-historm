import streamlit as st
import pandas as pd
import plotly.express as px


def HI82():
    st.set_page_config(page_title='HI82 Temperature Data',
                       page_icon=':bar_chart:', layout='centered')
    st.title('HI82 Temperature Data')
    file = st.file_uploader('Upload xlsx file with HI82 data', type=['xlsx'])

    if file:
        df = pd.read_excel(file)
        df = df.loc[(df['Holtec/Casks/HI82/Average Temp'] > 0)]
        # Let the user select the minimum value
        min_val = st.number_input(
            'Enter the minimum value for Holtec/Environment/TIA/Value', value=df['Holtec/Environment/TIA/Value'].min())
        # Let the user select the maximum value
        max_val = st.number_input(
            'Enter the maximum value for Holtec/Environment/TIA/Value', value=df['Holtec/Environment/TIA/Value'].max())
        df = df[(df['Holtec/Environment/TIA/Value'] >= min_val) & (
            df['Holtec/Environment/TIA/Value'] <= max_val)]  # Filter DataFrame
        fig = px.scatter(df, x='t_stamp', y=[
                         'Holtec/Casks/HI82/Average Temp'], title='HI82 Temperature Data')
        # Set y-axis limits and title
        fig.update_yaxes(range=[0, 100], title_text='Temperature (°C)')
        fig.update_xaxes(title_text='Date - Time')  # Set x-axis title
        st.plotly_chart(fig)


HI82()
