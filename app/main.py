import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from utils import plot_correlation_heatmap, plot_time_series, plot_wind_rose, detect_outliers, clean_dataset, plot_wind_direction_distribution, plot_temperature_vs_humidity, plot_temperature_trends, plot_pair_plot

# Constants
# DATA_FOLDER = "../data/original_datasets/"
DATA_FOLDER = "data/original_datasets/"
CLEANED_FOLDER = "data/cleaned_datasets/"

DATASETS = {
    "Benin Malanville": os.path.join(DATA_FOLDER, "benin-malanville.csv"),
    "Sierra Leone Bumbuna": os.path.join(DATA_FOLDER, "sierraleone-bumbuna.csv"),
    "Togo Dapaong QC": os.path.join(DATA_FOLDER, "togo-dapaong_qc.csv"),
}

# Cache data loading
@st.cache_data
# Utility: Load dataset
def load_data(data_path):
    """Load dataset from a CSV file."""
    try:
        return pd.read_csv(data_path)
    except Exception as e:
        st.error(f"Failed to load data from {data_path}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure
    
# Load and clean all datasets
@st.cache_data
def load_and_clean_all_datasets():
    """Load, clean, and save all datasets."""
    uncleaned_data = {}
    cleaned_data = {}
    for name, path in DATASETS.items(): 
        raw_data = load_data(path)  # Load raw data
        uncleaned_data[name] = raw_data
        cleaned_path = os.path.join(CLEANED_FOLDER, f"{name.lower().replace(' ', '_')}_cleaned.csv")
        cleaned_data[name] = clean_dataset(raw_data, output_path=cleaned_path) 
    return cleaned_data, uncleaned_data

# Main workflow
all_cleaned_data, all_uncleaned_data = load_and_clean_all_datasets()

# Sidebar for dataset selection
selected_dataset_name = st.sidebar.selectbox("Select Dataset", list(DATASETS.keys()))
# selected_dataset = all_cleaned_data.get(selected_dataset_name, pd.DataFrame())
selected_dataset = all_uncleaned_data.get(selected_dataset_name, pd.DataFrame())

# App Title
st.title(f"Solar Farm Data Analysis Dashboard for {selected_dataset_name}")
# st.write(f"Dataset: {selected_dataset_name}", selected_dataset)

# Create Tabs
tab_overview, tab_eda, tab_visuals, tab_advanced = st.tabs(["Overview", "EDA", "Visualizations", "Advanced Analysis"])

# Overview Tab
with tab_overview:
    st.header("Overview")
    st.write(f"""
    This dashboard provides a detailed analysis of the {selected_dataset_name} dataset.
    Navigate to different sections to explore data insights, trends, and advanced analysis.
    """)

# EDA Tab
with tab_eda:
    st.header("Exploratory Data Analysis")
    st.write("**Data Summary:**")
    st.write(selected_dataset.describe())
    st.write("**Missing Values:**")
    st.write(selected_dataset.isnull().sum())
    st.write("**Duplicates:**")
    st.write(selected_dataset.duplicated().sum())
# Visualizations Tab
with tab_visuals:
    st.header("Data Visualizations")

    # Correlation Heatmap
    st.subheader("Correlation Heatmap")
    try:
        plot_correlation_heatmap(selected_dataset)
    except Exception as e:
        st.error(f"Error plotting correlation heatmap: {e}")

    # Time Series Trends
    if 'Timestamp' in selected_dataset.columns:
        st.subheader("Time Series Trends")
        try:
            plot_time_series(selected_dataset)
        except Exception as e:
            st.error(f"Error plotting time series trends: {e}")

    # Wind Rose
    if {'WD', 'WS'}.issubset(selected_dataset.columns):
        st.subheader("Wind Rose")
        try:
            plot_wind_rose(selected_dataset)
        except Exception as e:
            st.error(f"Error plotting wind rose: {e}")

    # Wind Direction Distribution
    if 'WD' in selected_dataset.columns:
        st.subheader("Wind Direction Distribution")
        try:
            plot_wind_direction_distribution(selected_dataset)
        except Exception as e:
            st.error(f"Error plotting wind direction distribution: {e}")

# Advanced Analysis Tab
with tab_advanced:
    st.header("Advanced Analysis")
    
    # Z-score and Outlier Detection
    st.subheader("Outlier Detection")
    outlier_columns = ['GHI', 'DNI', 'DHI']
    if all(col in selected_dataset.columns for col in outlier_columns):
        try:
            valid_data = selected_dataset[outlier_columns]
            outliers = detect_outliers(valid_data, outlier_columns) 
            st.write(f"Number of outliers detected: {len(outliers)}")
            fig, ax = plt.subplots()
            sns.boxplot(data=valid_data, ax=ax)
            plt.title("Boxplot of GHI, DNI, DHI (Outlier Detection)")
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error detecting outliers: {e}")

    # Temperature and Humidity Analysis
    if {'Tamb', 'RH'}.issubset(selected_dataset.columns):
        st.subheader("Temperature vs. Relative Humidity")
        try:
            plot_temperature_vs_humidity(selected_dataset)
        except Exception as e:
            st.error(f"Error plotting temperature vs. humidity: {e}")

    # Module Temperature Analysis
    module_columns = ['TModA', 'TModB', 'Tamb']
    if all(col in selected_dataset.columns for col in module_columns):
        st.subheader("Temperature Trends Across Modules")
        try:
            plot_temperature_trends(selected_dataset)
        except Exception as e:
            st.error(f"Error plotting temperature trends: {e}")

    # Pair Plot
    analysis_columns = ['GHI', 'DNI', 'DHI', 'Tamb', 'RH', 'WS']
    available_columns = [col for col in analysis_columns if col in selected_dataset.columns]
    if available_columns:
        st.subheader("Pair Plot of Key Variables")
        try:
            plot_pair_plot(selected_dataset)
        except Exception as e:
            st.error(f"Error plotting pair plot: {e}")
