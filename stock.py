import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image

# -------- CONFIG -------- 
CSV_FILE = "registrations.csv"
ADMIN_PASSWORD = st.secrets["app"]["admin_password"]
EMAIL_ADDRESS = st.secrets["email"]["address"]
EMAIL_PASSWORD = st.secrets["email"]["password"]
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"

# -------- FUNCTIONS --------
def send_confirmation_email(to_email, name):
    subject = "Workshop Registration Confirmation"
    body = f"""
Hi {name},

Thank you for registering for the Stock Market Workshop.
We have received your registration successfully.

Regards,
Workshop Team
"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Error sending confirmation email: {e}")
        return False

def save_registration(data: dict):
    df = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

def get_registration_count():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return len(df)
    return 0

def delete_all_registrations():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        return True
    return False

# -------- PAGES --------
def payment_page():
    st.title("💳 Payment Section")
    st.write("Please scan the QR code below to make your payment:")

    try:
        qr_image = Image.open("payment_qr.jpg")
        st.image(qr_image, caption="Scan to Pay", use_container_width=False, width=300)
    except FileNotFoundError:
        st.error("QR code image not found. Please upload 'payment_qr.jpg' to your repo.")

    transaction_id = st.text_input("Enter UPI Transaction Id (12 digits only)", max_chars=12)

    if not st.session_state.get("payment_confirmed", False):
        uploaded_file = st.file_uploader("Upload payment screenshot here", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded payment screenshot", use_container_width=True)
            if st.button("Proceed"):
                if not (transaction_id.isdigit() and len(transaction_id) == 12):
                    st.error("⚠ Please enter a valid 12-digit numeric UPI Transaction Id before proceeding.")
                else:
                    if "user_email" in st.session_state and "user_name" in st.session_state:
                        sent = send_confirmation_email(st.session_state["user_email"], st.session_state["user_name"])
                        if sent:
                            st.success("✅ Registration successful and details have been sent to your mail")
                        else:
                            st.error("❌ Failed to send registration email.")

                        del st.session_state["user_email"]
                        del st.session_state["user_name"]

                    st.session_state["payment_confirmed"] = True
                    st.session_state["show_proceed"] = True
    else:
        st.info("You have already completed payment and registration.")

    if st.session_state.get("show_proceed", False):
        st.success("🎉 Process completed!")


def admin_page():
    st.title("🔑 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success(f"✅ Total Registered Participants: {get_registration_count()}")

        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Registrations CSV",
                data=csv,
                file_name="registrations.csv",
                mime="text/csv"
            )

            st.subheader("🗑 Delete All Registrations")
            confirm_password = st.text_input("Re-enter Admin Password to Confirm Deletion:", type="password", key="delete_confirm")
            if st.button("⚠ Confirm Delete", type="primary"):
                if confirm_password == ADMIN_PASSWORD:
                    if delete_all_registrations():
                        st.success("✅ All registration data has been deleted.")
                        st.rerun()
                    else:
                        st.info("No registration data found.")
                else:
                    st.error("❌ Incorrect password. Deletion cancelled.")

        else:
            st.info("No registrations yet.")
    elif password:
        st.error("Incorrect password")

def payment_page():
    st.title("💳 Payment Section")
    st.write("Please scan the QR code below to make your payment:")

    try:
        qr_image = Image.open("payment_qr.jpg")
        st.image(qr_image, caption="Scan to Pay", use_container_width=False, width=300)
    except FileNotFoundError:
        st.error("QR code image not found. Please upload 'payment_qr.jpg' to your repo.")

    transaction_id = st.text_input("Enter UPI Transaction Id (12 digits only)", max_chars=12)

    if not st.session_state.get("payment_confirmed", False):
        uploaded_file = st.file_uploader("Upload payment screenshot here", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Uploaded payment screenshot", use_container_width=True)
            if st.button("Confirm to Upload"):
                if not (transaction_id.isdigit() and len(transaction_id) == 12):
                    st.error("⚠ Please enter a valid 12-digit numeric UPI Transaction Id before confirming.")
                else:
                    st.session_state["payment_confirmed"] = True
                    st.success("✅ Payment confirmed! Thank you for registering.")

                    if "user_email" in st.session_state and "user_name" in st.session_state:
                        sent = send_confirmation_email(st.session_state["user_email"], st.session_state["user_name"])
                        if sent:
                            st.success("📧 Registration confirmation email sent successfully!")
                        else:
                            st.error("❌ Failed to send registration email.")

                        del st.session_state["user_email"]
                        del st.session_state["user_name"]

                    st.session_state["show_proceed"] = True
    else:
        st.success("✅ Payment has been confirmed. Thank you!")

    if st.session_state.get("show_proceed", False):
        if st.button("Proceed"):
            st.success("🎉 You have successfully completed the registration and payment process!")

# -------- APP NAVIGATION --------
if "registered" not in st.session_state:
    st.session_state["registered"] = False
if "payment_confirmed" not in st.session_state:
    st.session_state["payment_confirmed"] = False
if "show_proceed" not in st.session_state:
    st.session_state["show_proceed"] = False

menu = st.sidebar.selectbox("Select Mode", ["Register", "Admin"])

if menu == "Register":
    if st.session_state["registered"]:
        payment_page()
    else:
        registration_page()
elif menu == "Admin":
    admin_page()
