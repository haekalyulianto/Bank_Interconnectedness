from pyvis.network import Network
import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict
import warnings
warnings.simplefilter(action='ignore')
from streamlit_option_menu import option_menu
import util
import streamlit as st
import streamlit.components.v1 as components

# Konfigurasi Halaman
st.set_page_config(page_title="Interconnectedness",
                   page_icon=":art:", layout="wide")

# Tombol Refresh
do_refresh = st.sidebar.button('Refresh')

# Konfigurasi Pilihan Menu
selected = option_menu(
    menu_title=None,
    options=["Data Bank", "Data Siklik"],
    icons=["newspaper", "bank"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",)

# Inisialisasi Preprocess biar ga selalu preprcoess kalau di-rerun
if 'df2' not in st.session_state:
    df1 = pd.read_excel('Data Penempatan Dana Jan - Mei 2022.xlsx')
    df2 = pd.read_excel('LBU Rasio Alat Likuid Mar 2022.xlsx')

    periode = '2022-03-31'
    df3 = df1[(df1['Periode Data'] == periode)]
    df3 = df3.reset_index(drop=True)

    df4 = pd.read_excel('LBU Rasio Alat Likuid Mar 2022.xlsx')
    df4.to_csv('AL_Mar22.csv', index=False)

    df4 = pd.read_csv('AL_Mar22.csv')
    df4 = df4[['Sandi Bank', 'Penem Bank Lain IDR', 'Kewajiban Bank Lain IDR', 'Total AL']]

    df5 = util.inputo(df3, df4)

    df5 = util.calculate_penempatan_total(df5)

    df5 = df5[[ 'BankPelapor', 'BankTujuan', 'Jumlah Bulan Laporan', 'Persentase Penempatan', 'Total Penempatan',
            'Total Kewajiban', 'Penempatan/AL', 'Kewajiban/AL']]
    df5 = df5[df5['Jumlah Bulan Laporan'] > 0]

    df5 = df5.sort_values(by = ['BankPelapor'])
    df5 = df5.reset_index(drop=True)

    st.session_state['df2'] = df2
    st.session_state['df5'] = df5

if selected == "Data Bank":

    # Sunting Sidebar
    st.sidebar.image("LPS.png", output_format='PNG')
    #nama_bank = st.sidebar.text_input('Pencarian Kode Bank :')
    nama_bank = st.sidebar.selectbox('Pencarian Nama Bank',(st.session_state['df2']['Nama Bank']))
    bank_level = st.sidebar.number_input('Masukkan Level : ', value=1, step=1)
        
    # Konfigurasi Web
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'

    # Menjalankan Analisis Sentimen Berita
    if st.sidebar.button('Run'):
        st.header("Hasil Analisis Interconnectedness Bank")

        st.success('Hasil Analisis Interconnectedness Bank : ' + nama_bank + ' Level : ' + str(bank_level))
        util.view_data_from_bank_level(st.session_state['df5'], nama_bank, bank_level, st.session_state['df2'])
        file = open('graph_bank_level.html', 'r', encoding='utf-8')
        source = file.read()
        components.html(source, height = 500)

        st.success('Hasil Analisis Interconnectedness Keseluruhan')
        util.view_all(st.session_state['df5'])
        file = open('graph_all.html', 'r', encoding='utf-8')
        source = file.read()
        components.html(source, height = 500)

if selected == "Data Siklik":
    df5 = st.session_state['df5']
    min_persentase_penempatan = df5['Persentase Penempatan'].min()
    max_persentase_penempatan = df5['Persentase Penempatan'].max()
    min_penempatan_per_al = df5['Penempatan/AL'].min()
    max_penempatan_per_al = df5['Penempatan/AL'].max()
    min_kewajiban_per_al = df5['Kewajiban/AL'].min()
    max_kewajiban_per_al = df5['Kewajiban/AL'].max()

    st.sidebar.image("LPS.png", output_format='PNG')
    filter_persentase_penempatan_min, filter_persentase_penempatan_max = st.sidebar.slider('Persentase Penempatan : ', min_persentase_penempatan, max_persentase_penempatan, (min_persentase_penempatan, max_persentase_penempatan))
    filter_penempatan_per_al_min, filter_penempatan_per_al_max = st.sidebar.slider('Penempatan/AL : ', min_penempatan_per_al, max_penempatan_per_al, (min_penempatan_per_al, max_penempatan_per_al))
    filter_kewajiban_per_al_min, filter_kewajiban_per_al_max = st.sidebar.slider('Kewajiban/AL : ', min_kewajiban_per_al, max_kewajiban_per_al, (min_kewajiban_per_al, max_kewajiban_per_al))
    cycle_num = st.sidebar.number_input('Masukkan Jumlah Siklik : ', value=10, step=1)
    cycle_len = st.sidebar.number_input('Masukkan Panjang Siklik : ', value=5, step=1)

    if st.sidebar.button('Run'):
        st.header("Hasil Analisis Interconnectedness Siklik Bank")

        df6 = util.filter_bank(st.session_state['df5'], min_persentase_penempatan, max_persentase_penempatan, min_penempatan_per_al, max_penempatan_per_al, min_kewajiban_per_al, max_kewajiban_per_al)
        df7 = util.view_data_cycle_all(df6, cycle_num, cycle_len, st.session_state['df2'])

        col1, col2 = st.columns(2)

        with col1:
            st.success('Ilustrasi Hasil Analisis Tingkat Sistemik')
            file = open('graph_cycle.html', 'r', encoding='utf-8')
            source = file.read()
            components.html(source, height=1000)

        with col2:
            st.success('Tabel Hasil Analisis Tingkat Sistemik')
            st.dataframe(data=df7, height=1000)