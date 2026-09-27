import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


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
    return df
    


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

def top10_agents(df):
    top_agents = df['SellerG'].value_counts().head(10).reset_index()
    top_agents.columns = ['Agent Name', 'Properties Sold']

    fig_bar, ax_bar = plt.subplots(figsize=(6, 4.2))
        
    sns.barplot(data=top_agents, x='Properties Sold', y='Agent Name', palette='viridis', ax=ax_bar)
        
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
    * **Fakta Anomali:** Properti ini memuncak di harga **AUD {outlier_1['Price']:,.0f}**. Ini merupakan nilai tertinggi dalam dataset yang melenceng jauh dari rata-rata harga pasar wajar.

    **2. Anomali "Suburban Mansion" (Pinggiran Kota Berharga Tinggi)**
    * **Lokasi Properti:** {outlier_2['Address']}, {outlier_2['Suburb']}
    * **Spesifikasi:** Tipe **'{outlier_2['Type_Full']}'** dengan {int(outlier_2['Rooms'])} kamar tidur.
    * **Jarak ke CBD:** **{outlier_2['Distance']} km**.
    * **Fakta Anomali:** Meskipun letaknya sangat jauh dari pusat bisnis (>30 km), properti ini menembus harga fantastis sebesar **AUD {outlier_2['Price']:,.0f}**. Ini merupakan ketidakwajaran, mengingat area radius sejauh ini umumnya didominasi oleh perumahan harga terjangkau.
    """)

def main():
    st.title('Melbourne Housing Data Analytics')
    df = load_data()

    st.write('### Data Summary')
    st.dataframe(df.head())

    st.write('---')
    st.write('## Visualization 01')

    st.write('#### 1. Median Price by Rooms')
    plot_median_price_vs_rooms(df)

    st.write('#### 2. Price vs Distance to CBD')
    plot_price_vs_distance(df)

    st.write('## Visualization 04')
    st.write('#### Market Business Players & Pricing Anomalies')
    st.write("#### 1. Bar Chart: Top 10 Property Agents by Properties Sold")
    top10_agents(df)
    st.write("#### 2. Scatter Chart: Distance vs Price (Seaborn)")
    scatter_chart_distance_vs_price(df)
    anomaly_insights(df)


if __name__ == '__main__':
    main()