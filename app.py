import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

def load_data():
    df = pd.read_csv('melb_clean.csv')
    
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['YearMonth'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    
    return df

# PUNYA THANIA
def plot_median_price_vs_rooms(df):
    median_df = df.groupby('Rooms')['Price'].median().reset_index()

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = sns.color_palette('Blues', n_colors=len(median_df))

    ax.bar(
        median_df['Rooms'].astype(str),
        median_df['Price'] / 1e6,
        color=colors,
        edgecolor='black',
        linewidth=0.5,
    )

    ax.set_title('Median Price by Rooms')
    ax.set_xlabel('Number of Rooms')
    ax.set_ylabel('Median Price (Millions AUD)')

    st.pyplot(fig)

    counts_df = df.groupby('Rooms')['Price'].count().reset_index(name='Count')
    median_df = median_df.merge(counts_df, on='Rooms')

    st.dataframe(median_df)

def plot_price_vs_distance(df):
    type_labels = {'h': 'House', 'u': 'Unit', 't': 'Townhouse'}
    plot_df = df.copy()
    plot_df['Type'] = plot_df['Type'].map(type_labels)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.scatterplot(data=plot_df, x='Distance', y='Price', hue='Type',
                     hue_order=['House', 'Unit', 'Townhouse'],
                     palette='Set2', alpha=0.5, ax=ax)
    ax.set_yscale('log')
    ax.set_title('Price vs Distance to CBD (Central Business District)')
    ax.set_xlabel('Distance to CBD (km)')
    ax.set_ylabel('Price (AUD, Log Scale)')
    ax.legend(title='Type')

    st.pyplot(fig)

    corr = df['Price'].corr(df['Distance'])
    med_type = df.groupby('Type')['Price'].median()


# PUNYA ELIZ
def plot_heatmap_volume(df):
    st.write('#### 1. Transaction Volume Heatmap')
    heatmap_data = pd.crosstab(df['Year'], df['Month'])
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heatmap_data, cmap='Blues', annot=True, fmt="d", linewidths=.5, ax=ax)
    ax.set_title("Sales Concentration (Month vs Year)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Year")
    st.pyplot(fig)

def plot_trend_region(df):
    st.write('#### 2. Median Price Trend by Region')
    top_regions = df['Regionname'].value_counts().head(3).index
    df_top = df[df['Regionname'].isin(top_regions)]
    trend_region = df_top.groupby(['YearMonth', 'Regionname'])['Price'].median().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=trend_region, x='YearMonth', y='Price', hue='Regionname', palette='Set2', linewidth=2, ax=ax)
    ax.set_title("Price Comparison of Top 3 Regions")
    ax.set_ylabel("Median Price (AUD)")
    ax.set_xlabel("Time (Year-Month)")
    ax.grid(True, linestyle='--', alpha=0.5)
    st.pyplot(fig)

def plot_date_vs_price(df):
    st.write('#### 3. Price Distribution Over Time')
    fig, ax = plt.subplots(figsize=(10, 5))
    threshold = df['Price'].quantile(0.99)
    colors_accent = ['#e74c3c' if p > threshold else '#bdc3c7' for p in df['Price']] 
    
    ax.scatter(df['Date'], df['Price'], c=colors_accent, alpha=0.6, edgecolor='none')
    ax.set_yscale('log')
    ax.set_title("Property Price Distribution (Top 1% Highlighted)")
    ax.set_ylabel("Price (AUD, Log Scale)")
    ax.set_xlabel("Transaction Date")
    ax.grid(True, linestyle='--', alpha=0.4)
    st.pyplot(fig)



def main():
    st.set_page_config(layout="wide") 
    st.title('Melbourne Housing Data Analytics')
    df = load_data()

    st.write('### Data Summary')
    st.dataframe(df.head())

    st.write('---')
    st.write('## Visualization: NATHANIA')

    st.write('#### 1. Median Price by Rooms')
    plot_median_price_vs_rooms(df)

    st.write('#### 2. Price vs Distance to CBD')
    plot_price_vs_distance(df)

    st.write('---')
    st.write('## Visualization: ELIZABETH')
    
    col1, col2 = st.columns(2)
    with col1:
        plot_heatmap_volume(df)
    with col2:
        plot_trend_region(df)
        
    plot_date_vs_price(df)

if __name__ == '__main__':
    main()