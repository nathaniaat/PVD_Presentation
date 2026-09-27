import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from matplotlib import ticker
from matplotlib.ticker import ScalarFormatter

st.set_page_config(
    page_title='Melbourne Housing Data Analytics Dashboard',
    layout='centered',
)
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.family'] = 'sans-serif'

custom_colors = [
    '#8B0000',  # Merah pekat (terendah)
    '#E57373',
    '#FFB74D',
    '#FFF176',
    '#DCE775',
    '#AED581',
    '#81C784',
    '#66BB6A'   # Hijau (tertinggi)
]

region_order = [
    'Western Victoria',
    'Northern Victoria',
    'Eastern Victoria',
    'Eastern Metropolitan',
    'South-Eastern Metropolitan',
    'Western Metropolitan',
    'Northern Metropolitan',
    'Southern Metropolitan'
]
def load_data():
    return pd.read_csv('melb_clean.csv')

def plot_bar_chart(df):
    # Prepare Data
    region_volume = (
        df.groupby('Regionname')
        .size()
        .reset_index(name='Volume')
        .sort_values(by='Volume', ascending=True)
    )
    
    # Create Figure & Axis
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.barplot(
        data=region_volume,
        x='Volume',
        y='Regionname',
        palette=custom_colors,
        ax=ax
    )
    ax.set_xlabel('') 
    ax.set_ylabel('') 
    ax.tick_params(axis='y', labelsize=11)
    ax.tick_params(axis='x', labelsize=10)
    
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(
            f'{int(width):,}',
            (width, p.get_y() + p.get_height() / 2.),
            ha='left',
            va='center',
            xytext=(8, 0),
            textcoords='offset points',
            fontsize=11
        )  
    sns.despine(top=True, right=True)
    plt.tight_layout()
    return fig

def plot_line_chart(df):
    trend_data = (
        df.groupby(['Year Quarter', 'Regionname'])
        .size()
        .reset_index(name='Volume')
    )
    trend_data['Year Quarter'] = trend_data['Year Quarter'].astype(str)
    color_palette = dict(zip(region_order, custom_colors))

    fig, ax = plt.subplots(figsize=(12, 4.5))
    
    sns.lineplot(
        data=trend_data,
        x='Year Quarter',
        y='Volume',
        hue='Regionname',
        hue_order=region_order,
        palette=color_palette,
        marker='o',
        linewidth=2.5,
        ax=ax
    )
    
    ax.set_yscale('log')
    ax.set_xlabel('') 
    ax.set_ylabel('') 
    ax.tick_params(axis='both', labelsize=10)
    plt.xticks(rotation=45)
    
    ax.legend(
        title='',                     
        bbox_to_anchor=(1.02, 1),      
        loc='upper left',
        frameon=False,
        fontsize=10                
    )
    
    ax.yaxis.set_major_locator(ticker.LogLocator(base=10.0, subs=(1.0,)))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs=(2.0, 5.0)))
    ax.yaxis.set_minor_formatter(ScalarFormatter())
    
    ax.grid(True, which="both", ls="--", linewidth=0.5, alpha=0.5)
    sns.despine(top=True, right=True)
    plt.tight_layout()
    return fig

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

    st.pyplot(fig, use_container_width=True)

    counts_df = df.groupby('Rooms')['Price'].count().reset_index(name='Count')
    median_df = median_df.merge(counts_df, on='Rooms')

    st.dataframe(median_df, use_container_width=True)


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

    st.pyplot(fig, use_container_width=True)

    corr = df['Price'].corr(df['Distance'])
    med_type = df.groupby('Type')['Price'].median()


def main():
    st.title('Melbourne Housing (2016-2018) Data Analytics Dashboard')
    df = load_data()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Year Quarter'] = df['Date'].dt.to_period('Q')
    
    st.write('### Data Summary')
    st.dataframe(df.head())

    st.divider()
    st.write('## Housing Volume Trends By Region (2016-2018)')
    
 
    st.markdown('### Housing Volume Comparison')
    st.write('')
    st.pyplot(plot_bar_chart(df), use_container_width=True)
    st.write('')
    st.markdown('### Changes in Housing Volume Trend')
    st.text('Melbourne housing is aggregated by calendar quarters:\n' 
        '1. Q1: January until March\n' 
        '2. Q2: April until June\n' 
        '3. Q3: July until September\n' 
        '4. Q4: October until December')
    st.pyplot(plot_line_chart(df), use_container_width=True)

    st.write('---')
    st.write('## Visualization 01')

    st.write('#### 1. Median Price by Rooms')
    plot_median_price_vs_rooms(df)

    st.write('#### 2. Price vs Distance to CBD')
    plot_price_vs_distance(df)

if __name__ == '__main__':
    main()