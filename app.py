import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import numpy as np


# Set page configuration
st.set_page_config(
    page_title="CORD-19 Dataset Explorer",
    page_icon="📊",
    layout="wide"
)


def load_data():
    """Load data from metadata_first_10000.csv for analysis"""
    try:
        df = pd.read_csv("metadata.csv")
        st.success(f"✅ Loaded {len(df):,} rows from metadata_first_10000.csv")
        return df
    except FileNotFoundError:
        st.error("❌ metadata.csv not found. Please ensure the file exists.")
        return None
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")
        return None

def plot_publications_over_time(df, year_col):
    """Plot publications over time"""
    if year_col not in df.columns:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    yearly_data = df[year_col].value_counts().sort_index()
    yearly_data = yearly_data[yearly_data.index.notna()]
    
    if len(yearly_data) > 0:
        ax.plot(yearly_data.index, yearly_data.values, marker='o', linewidth=2, markersize=4)
        ax.set_title('Publications Over Time', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Publications')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        return fig
    return None

def plot_top_journals(df, journal_col, top_n=10):
    """Plot top publishing journals"""
    if journal_col not in df.columns:
        return None
        
    fig, ax = plt.subplots(figsize=(10, 6))
    top_journals = df[journal_col].value_counts().head(top_n)

    if len(top_journals) > 0:
        bars = ax.barh(range(len(top_journals)), top_journals.values)
        ax.set_yticks(range(len(top_journals)))
        ax.set_yticklabels([journal[:40] + '...' if len(journal) > 40 else journal 
                           for journal in top_journals.index])
        ax.set_title(f'Top {top_n} Publishing Journals', fontweight='bold')
        ax.set_xlabel('Number of Publications')
        return fig
    return None

def show_dashboard(df):
    """Display dashboard with metrics and visualizations"""
    st.header("Dashboard Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Papers", f"{len(df):,}")
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Missing Values", f"{df.isnull().sum().sum():,}")
    with col4:
        st.metric("Data Types", f"{df.dtypes.nunique()}")
    
    # Find relevant columns
    year_cols = [col for col in df.columns if 'year' in col.lower()]
    journal_cols = [col for col in df.columns if any(kw in col.lower() for kw in ['journal', 'source'])]
    
    # Visualizations
    if year_cols:
        fig = plot_publications_over_time(df, year_cols[0])
        if fig:
            st.pyplot(fig)
    
    if journal_cols:
        col1, col2 = st.columns(2)
        with col1:
            top_n = st.slider("Number of journals to show:", 5, 20, 10)
            fig = plot_top_journals(df, journal_cols[0], top_n)
            if fig:
                st.pyplot(fig)
        
        with col2:
            journal_counts = df[journal_cols[0]].value_counts().head(10)
            st.write("**Top 10 Journals**")
            st.dataframe(journal_counts)

def show_data_explorer(df):
    """Interactive data exploration"""
    st.header("Data Explorer")
    
    # Filters
    st.sidebar.subheader("Filters")
    selected_cols = st.sidebar.multiselect(
        "Select columns:",
        options=df.columns.tolist(),
        default=df.columns.tolist()[:5]
    )
    
    sample_size = st.sidebar.slider("Sample size:", 1, 100, 10)
    
    # Display data
    if selected_cols:
        st.dataframe(df[selected_cols].head(sample_size))
    
    # Statistics
    st.subheader("Dataset Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Types**")
        st.write(df.dtypes.value_counts())
    
    with col2:
        st.write("**Missing Values (Top 10)**")
        missing = df.isnull().sum().sort_values(ascending=False).head(10)
        st.write(missing[missing > 0])

def main():
    """Main application"""
    st.title("CORD-19 Dataset Explorer")
    
    # Load data
    df = load_data()
    if df is None:
        return  # Stop if data loading failed
    
    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to:", ["Dashboard", "Data Explorer", "About"])
    
    if page == "Dashboard":
        show_dashboard(df)
    elif page == "Data Explorer":
        show_data_explorer(df)
    else:
        st.header("About")
        st.write("CORD-19 Dataset Explorer - Analyze COVID-19 research metadata")

if __name__ == "__main__":

    main()
