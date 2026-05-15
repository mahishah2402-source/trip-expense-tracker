import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# 1. Page Setup
st.set_page_config(page_title="Trip Expense Tracker", page_icon="✈️")

st.title("✈️ Trip Expense Tracker")
st.write("Tracking expenses for: **Mahi, Tinu, and Manya**")

# --- 2. INPUT BUTTON ---
# Update this with your new Trip Google Form link
form_url = "https://docs.google.com/spreadsheets/d/1Uss18LdeI-OChCmup49UqiwvoANgzCm6h3zCrewmBYw/edit?usp=sharing"
st.link_button("➕ Log Trip Expense", form_url, type="primary", use_container_width=True)

st.divider()

# --- 3. DATA LOADING ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)

    if not df.empty:
        # Data Cleaning
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], dayfirst=True)
        df['Date'] = df['Timestamp'].dt.strftime('%d-%m-%Y')

        # --- 4. OVERALL SUMMARY ---
        total_trip_cost = df["Amount"].sum()
        st.metric("Total Trip Cost", f"₹{total_trip_cost:,.2f}")

        # --- 5. INDIVIDUAL BREAKDOWN (Who Paid What?) ---
        st.subheader("👤 Spending by Person")
        
        # Ensure the column in your Google Sheet is named 'Paid By' 
        # and contains the names Mahi, Tinu, or Manya
        person_sum = df.groupby("Paid By")["Amount"].sum().reset_index()
        
        # Create a Pie Chart for People
        fig_people = px.pie(
            person_sum, 
            values='Amount', 
            names='Paid By', 
            title="Contribution Split",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4
        )
        st.plotly_chart(fig_people, use_container_width=True)

        # --- 6. CATEGORY BREAKDOWN ---
        st.subheader("📊 Spending by Category")
        cat_sum = df.groupby("Category")["Amount"].sum().reset_index()
        
        fig_cat = px.pie(
            cat_sum, 
            values='Amount', 
            names='Category', 
            color_discrete_sequence=px.colors.sequential.Teal_r,
            hole=0.4
        )
        st.plotly_chart(fig_cat, use_container_width=True)

        # --- 7. DETAILED HISTORY ---
        st.divider()
        st.subheader("📜 Trip Log")
        display_df = df[['Date', 'Paid By', 'Category', 'Amount']]
        if 'Note' in df.columns:
            display_df = df[['Date', 'Paid By', 'Category', 'Amount', 'Note']]
            
        st.dataframe(display_df.sort_index(ascending=False), use_container_width=True)
    
    else:
        st.info("No trip expenses logged yet!")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Ensure your Sheet has columns: 'Timestamp', 'Paid By', 'Category', and 'Amount'.")
