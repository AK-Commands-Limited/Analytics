import sqlite3
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Connecting Sqlite
conn = sqlite3.connect('market_prices.db')
cursor = conn.cursor()

# Page Introduction
st.set_page_config(page_title="site of HIGHTECH by AK")
st.title("Market Prices")
st.sidebar.header("Select Commodity")

# Getting unique commodity list
@st.cache_data
def get_unique_commodity():
    conn = sqlite3.connect("market_prices.db")
    query = """
        SELECT DISTINCT Commodity 
        FROM main
        WHERE Commodity IS NOT NULL
        ORDER BY Commodity;
    """
    commodity_df = pd.read_sql_query(query, conn)
    conn.close()

    commodity_list = commodity_df['Commodity'].dropna().drop_duplicates().tolist()
    return commodity_list

# Loading data for selected commodity
@st.cache_data
def load_commodity_data(Commodity):
    conn = sqlite3.connect("market_prices.db")
    query = """
        SELECT *
        FROM main
        WHERE Commodity = ?
        ORDER BY Date;
    """
    
    df = pd.read_sql_query(query, conn, params=(Commodity,))
    conn.close()

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.drop_duplicates(subset=["Date"], keep="first")
    return df

available_commodity = get_unique_commodity()

if not available_commodity:
    st.error("No Data Found")
else:
   selected_commodity = st.sidebar.selectbox(
        "Select Commodity", 
        options=available_commodity
   )       

   df = load_commodity_data(selected_commodity)         

   st.subheader(f"Trends of {selected_commodity}")
                     
   if df.empty:         
         st.warning(f"No present data, we'll inform you when it's updated")       

   else:
         # Create Plotly figure
         fig = go.Figure()

         # Add Maximum Price line
         fig.add_trace(go.Scatter(
             x=df["Date"], y=df["Maximum"], 
             mode='lines+markers', name='Maximum Price',
             line=dict(color='green', dash='dash')
         ))

         # Add Minimum Price line
         fig.add_trace(go.Scatter(
             x=df["Date"], y=df["Minimum"], 
             mode='lines+markers', name='Minimum Price',
             line=dict(color='red', dash='dash')
         ))

         # Add Average Price line
         fig.add_trace(go.Scatter(
             x=df["Date"], y=df["Average"], 
             mode='lines+markers', name='Average',
             line=dict(color='blue', dash='dash')
         ))

         # Chart layout and scroll bar (range slider)
         fig.update_layout(
             title=f"Trends of {selected_commodity}",
             xaxis_title="Arrival Date",
             yaxis_title="Modal Price",
             hovermode="x unified",
             height=550
         )

         # THIS ADDS THE SCROLL BAR AT THE BOTTOM
         fig.update_xaxes(rangeslider=dict(visible=True))

         # Render interactive chart in Streamlit
         st.plotly_chart(fig, use_container_width=True)
         
         with st.expander("View Raw Data"):
            st.dataframe(df, use_container_width=True)