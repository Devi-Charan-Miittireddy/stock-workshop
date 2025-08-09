import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ------------- CONFIGURATION -------------
CSV_FILE = "registrations.csv"
ADMIN_PASSWORD = "admin123"
PAYMENT_LINK = "https://example.com/payment"
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"

# ------------- SESSION STATE FLAGS -------------
if "registration_done" not in st.session_state:
    st.session_state.registration_done = False

# ------------- HELPER FUNCTIONS -------------
def save_registration(name, email, phone, workshop):
    df = pd.DataFrame([[name, email, phone, workshop, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                      columns=["Name", "Email", "Phone", "Workshop", "Timestamp"])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

def load_registrations():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["Name", "Email", "Phone", "Workshop", "Timestamp"])

def delete_all_data(password):
    if password == ADMIN_PASSWORD:
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
        return True
    return False

# ------------- STREAMLIT APP -------------
st.set_page_config(page_title="Stock Market Workshop", layout="wide")

menu = st.sidebar.radio("Navigation", ["Registration", "Admin"])

# ------------------ REGISTRATION PAGE ------------------
if menu == "Registration":
    st.title("📈 Stock Market Workshop Registration")

    st.markdown(
        '<div style="background-color:#ffeeba;padding:10px;border-radius:5px;color:#856404;">'
        '<b>⚠️ Warning:</b> Once you register, your details cannot be changed. Please double-check before submitting.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        workshop = st.selectbox("Select Workshop", ["Beginner", "Intermediate", "Advanced"])
        submit = st.form_submit_button("Register")

        if submit:
            if name and email and phone:
                save_registration(name, email, phone, workshop)
                st.session_state.registration_done = True
            else:
                st.error("Please fill all the details.")

    if st.session_state.registration_done:
        st.success("✅ Registration successful... You are being directed to payment section")
        st.markdown(f"[💳 Click here to proceed to payment]({PAYMENT_LINK})", unsafe_allow_html=True)
        st.markdown(f"[💬 Join our WhatsApp Group]({WHATSAPP_LINK})", unsafe_allow_html=True)

# ------------------ ADMIN PAGE ------------------
elif menu == "Admin":
    st.title("🔑 Admin Panel")

    admin_password = st.text_input("Enter Admin Password", type="password")
    if st.button("View Registrations"):
        if admin_password == ADMIN_PASSWORD:
            data = load_registrations()
            if not data.empty:
                st.dataframe(data)
            else:
                st.warning("No registrations found.")
        else:
            st.error("Incorrect password.")

    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    delete_password = st.text_input("Enter Admin Password to Delete All Data", type="password")
    if st.button("Delete All Data"):
        if delete_all_data(delete_password):
            st.success("All data deleted successfully.")
        else:
            st.error("Incorrect password or no data to delete.")
