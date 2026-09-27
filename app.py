import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st


def load_data():
    return pd.read_csv('melb_clean.csv')


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


if __name__ == '__main__':
    main()