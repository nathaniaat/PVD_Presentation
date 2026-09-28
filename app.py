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
    df = pd.read_csv("melb_clean.csv")
    type_mapping = {
            'br': 'Bedroom(s)',
            'h': 'House, Cottage, Villa, Semi, Terrace',
            'u': 'Unit, Duplex',
            't': 'Townhouse',
            'dev site': 'Development Site',
            'o res': 'Other Residential'
        }
    
    df['Type_Full'] = df['Type'].map(type_mapping).fillna(df['Type'])
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['YearMonth'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

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

    st.pyplot(fig, use_container_width=True)

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

    st.pyplot(fig, use_container_width=True)

    corr = df['Price'].corr(df['Distance'])
    med_type = df.groupby('Type')['Price'].median()

# PUNYA GAB
def top10_agents(df):
    top_agents = df['SellerG'].value_counts().head(10).reset_index()
    top_agents.columns = ['Agent Name', 'Properties Sold']
    agent_sales = df['SellerG'].value_counts()
    total_agents = len(agent_sales) 
    st.markdown(f"""
    *Ringkasan Pasar Ekosistem Agen:* 
    Terdapat total *{total_agents} agen properti terdaftar* di dalam dataset.  
    Analisis di bawah ini difokuskan secara spesifik pada *Top 10 Agen Raksasa* yang memegang kendali utama di pasar Melbourne.
    """)

    fig_bar, ax_bar = plt.subplots(figsize=(6, 4.2))
        
    sns.barplot(data=top_agents, x='Properties Sold', y='Agent Name', palette='viridis', ax=ax_bar)

    for i, p in enumerate(ax_bar.patches):
        ax_bar.annotate(
            f"{int(p.get_width()):,}",  # Teks yang ditampilkan (diformat dengan koma ribuan)
            (p.get_width() + 15, p.get_y() + p.get_height() / 2.), # Koordinat posisi teks (X, Y)
            va='center', # Membuat teks sejajar di tengah batang secara vertikal
            fontsize=10  # Ukuran teks
        )   

    ax_bar.set_title("Top 10 Agents by Volume")
    ax_bar.set_xlabel("Total Properties Sold")
    ax_bar.set_ylabel("")
    ax_bar.grid(axis='x', linestyle='--', alpha=0.5)
        
    plt.tight_layout()
    st.pyplot(fig_bar)

def scatter_chart_distance_vs_price(df):
    anomalies = df[df['Price'] >= 5000000] 
    normal_sample = df[df['Price'] < 5000000].sample(2000, random_state=42)
    df_scatter = pd.concat([normal_sample, anomalies])

    fig_scat, ax_scat = plt.subplots(figsize=(10, 5))
    
    sns.scatterplot(
        data=df_scatter, 
        x='Distance', 
        y='Price', 
        hue='Type_Full', 
        alpha=0.7, 
        palette='deep',
        ax=ax_scat
    )
    
    ax_scat.set_title("Correlation: Distance from CBD vs Price")
    ax_scat.set_xlabel("Distance to CBD (km)")
    ax_scat.set_ylabel("Price (AUD)")
    ax_scat.grid(True, linestyle="--", alpha=0.5)
    

    st.pyplot(fig_scat)
    
    
def anomaly_insights(df):
    """Fungsi untuk menampilkan teks penjelasan anomali secara dinamis (berdasarkan kalkulasi data)."""
    st.subheader("Outliers")
    
    # 1. Mencari Properti Termahal (Harga > 5 juta AUD)
    max_price_idx = df['Price'].idxmax()
    outlier_1 = df.loc[max_price_idx]
    
    df_far = df[df['Distance'] > 30]
    outlier_2 = df_far.loc[df_far['Price'].idxmax()]
    
    st.markdown(f"""
    Berdasarkan pemrosesan data, sistem secara otomatis mendeteksi titik-titik anomali (*outliers*) utama pada visualisasi *scatter plot* di atas:

    **1. Anomali Harga Ekstrem (The Ultimate Outlier)**
    * **Lokasi Properti:** {outlier_1['Address']}, {outlier_1['Suburb']}
    * **Spesifikasi:** Tipe **'{outlier_1['Type_Full']}'** dengan {int(outlier_1['Rooms'])} kamar tidur.
    * **Jarak ke CBD:** **{outlier_1['Distance']} km**.
    * **Fakta Anomali:** Properti ini memuncak di harga **AUD {outlier_1['Price']:,.0f}**. Ini merupakan nilai tertinggi dalam dataset dan menonjol sebagai *outlier* yang signifikan.

    **2. Anomali "Suburban Mansion" (Pinggiran Kota Berharga Tinggi)**
    * **Lokasi Properti:** {outlier_2['Address']}, {outlier_2['Suburb']}
    * **Spesifikasi:** Tipe **'{outlier_2['Type_Full']}'** dengan {int(outlier_2['Rooms'])} kamar tidur.
    * **Jarak ke CBD:** **{outlier_2['Distance']} km**.
    * **Fakta Anomali:** Meskipun letaknya sangat jauh dari pusat bisnis (>30 km), properti ini menembus harga fantastis sebesar **AUD {outlier_2['Price']:,.0f}**. 
    """)

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
    st.title('Melbourne Housing (2016-2018) Data Analytics Dashboard')
    df = load_data()
    
    st.write('### Data Summary')
    st.dataframe(df.head())
    df['Year Quarter'] = df['Date'].dt.to_period('Q')

    st.divider()
    st.markdown('#### Visualization: CLARA')
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

    st.write('---')
    st.write('## Visualization: GABRIELLE')
    st.write('#### Market Business Players & Pricing Anomalies')
    st.write("#### 1. Bar Chart: Top 10 Property Agents by Properties Sold")
    top10_agents(df)
    st.write("#### 2. Scatter Chart: Distance vs Price (Seaborn)")
    scatter_chart_distance_vs_price(df)
    anomaly_insights(df)
    

if __name__ == '__main__':
    main()