import streamlit as st
import pyodbc
import pandas as pd

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection(view):
    if view == 'ANTASENA':
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server}"
            + ";SERVER=" + st.secrets["db_server"]
            + ";DATABASE=" + st.secrets["db_database_antasena"]
            + ";UID=" + st.secrets["db_username"]
            + ";PWD=" + st.secrets["db_password"]
        )
    else:
        return pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server}"
            + ";SERVER=" + st.secrets["db_server"]
            + ";DATABASE=" + st.secrets["db_database_master"]
            + ";UID=" + st.secrets["db_username"]
            + ";PWD=" + st.secrets["db_password"]
        )

def get_data_penempatan():    
    conn = init_connection('ANTASENA')
    query = "SELECT * from [dbo].[vSAPIT_PenempatanDana_LastPeriode]"
    df = pd.read_sql(query, conn)
    return df

def get_data_al():    
    conn = init_connection('')
    query = "SELECT * from [dbo].[vSAPIT_AlatLiquidLBU_LastPeriode]"
    df = pd.read_sql(query, conn)
    return df

