#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Lightweight Streamlit app to analyzez netflix streaming behavior

weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


# Function to convert duration string to total seconds
def duration_to_seconds(duration):
    h, m, s = map(int, duration.split(':'))
    return h * 3600 + m * 60 + s

# Function to load and preprocess the data
def load_data(file):
    df = pd.read_csv(file)
    df['Start Time'] = pd.to_datetime(df['Start Time'])
    df['Duration (s)'] = df['Duration'].apply(duration_to_seconds)
    df['Month-Year'] = df['Start Time'].dt.to_period('M').astype(str)
    df['Week'] = df['Start Time'].dt.to_period('W').astype(str)
    df['Weekday'] = df['Start Time'].dt.day_name()
    return df

# Function to plot total hours watched per month
def plot_total_hours_per_month(df, user):
    monthly_data = df[df['Profile Name'] == user].groupby('Month-Year')['Duration (s)'].sum() / 3600
    fig = px.bar(monthly_data, x=monthly_data.index, y=monthly_data.values, labels={'x': 'Month-Year', 'y': 'Hours'}, title=f'Total Hours Watched per Month by {user}')
    st.plotly_chart(fig)

# Function to plot total hours watched per week
def plot_total_hours_per_week(df, user):
    weekly_data = df[df['Profile Name'] == user].groupby('Week')['Duration (s)'].sum() / 3600
    fig = px.bar(weekly_data, x=weekly_data.index, y=weekly_data.values, labels={'x': 'Week', 'y': 'Hours'}, title=f'Total Hours Watched per Week by {user}')
    st.plotly_chart(fig)

# Function to plot average hours watched per weekday
def plot_average_hours_per_weekday(df, user):
    weekday_data_hours_weekday = df[df['Profile Name'] == user].groupby('Weekday')['Duration (s)'].sum() / 3600
    total_hours_watched = weekday_data_hours_weekday.sum()
    # Calculate the fraction of hours watched per weekday as a percentage of the total hours
    weekday_data_fraction = (weekday_data_hours_weekday / total_hours_watched * 100).round(2)
    fig = px.bar(weekday_data_fraction, x=weekday_data_fraction.index, y=weekday_data_fraction.values, labels={'x': 'Weekday', 'y': '% of hours Watched'},
                title=f'Percent of Hours Watched per Weekday by {user}', 
                category_orders={'Weekday': weekday_order})
    st.plotly_chart(fig)

# Function to plot total monthly hours watched for all users
def plot_monthly_comparison(df):
    monthly_comparison = df.groupby(['Month-Year', 'Profile Name'])['Duration (s)'].sum().unstack().fillna(0) / 3600
    fig = go.Figure()
    for user in monthly_comparison.columns:
        fig.add_trace(go.Scatter(x=monthly_comparison.index, y=monthly_comparison[user], mode='lines+markers', name=user))
    fig.update_layout(title='Monthly Hours Watched Comparison', xaxis_title='Month-Year', yaxis_title='Hours')
    st.plotly_chart(fig)


# Streamlit app
def main():
    st.title('Netflix Streaming Behavior')

    st.markdown("""
                **To see your own data follow these steps:**

                1. Download your own Netflix data from https://www.netflix.com/account/getmyinfo. 
                >*You have to request your dataset, confirm it via email and then ~1 day later you can download it from that site.*

                2. Unpack the zip file and find the ViewingActivity.csv under the CONTENT_INTERACTION folder.
                3. Upload the ViewingActivity.csv file into the app and you'll have all users visualized from your account.""")
    
    # Data upload
    uploaded_file = st.file_uploader('Upload your CSV file', type='csv')

    # Use Uploaded data
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    # Load example data if user clicks button
    else:
        if st.button('Load Example Data'):
            df = load_data("example_data/ViewingActivity.csv")
            st.success('Example data loaded!')
        else:
            df = None
    
    # Show plots once data is loaded
    if df is not None:    
        users = df['Profile Name'].unique()
        st.write('### Data Preview')
        st.dataframe(df.head())
        
        for user in users:
            st.write(f'## Analysis for {user}')
            plot_total_hours_per_month(df, user)
            plot_total_hours_per_week(df, user)
            plot_average_hours_per_weekday(df, user)
        
        st.write('## Monthly Hours Watched Comparison')
        plot_monthly_comparison(df)

if __name__ == '__main__':
    main()
