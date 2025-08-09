import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# -------------------- CONFIGURATION --------------------
ADMIN_PASSWORD = "admin123"  # Change this
COLLECTION_NAME = "registrations"
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"
WHATSAPP_LINK = "https://chat.whatsapp.com/yourlink"

# -------------------- FIREBASE INIT --------------------
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")  # your firebase key file
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------- FUNCTIONS --------------------
def send_confirmation_email(to_email, name):
    subject = "Registration Successful"
    body = f"""
    Hello {name},

    Thank you for registering for the Stock Market Workshop.

    WhatsApp Group: {WHATSAPP_LINK}

    Regards,
    Event Team
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
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Email sending failed: {e}")
        return False

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Workshop Registration", layout="centered")

menu = st.sidebar.selectbox("Select Page", ["Registration", "Admin Panel"])

if menu == "Registration":
    st.title("📋 Stock Market Workshop Registration")

    # Registration form for one person only
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        submit_button = st.form_submit_button("Register")

    if submit_button:
        if not name or not email or not phone:
            st.error("Please fill all fields")
        else:
            reg_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "timestamp": datetime.now()
            }
            db.collection(COLLECTION_NAME).add(reg_data)
            st.success("Registration successful! Redirecting to payment...")
            send_confirmation_email(email, name)
            st.markdown(f"[Click here to Pay](https://yourpaymentlink.com)")

elif menu == "Admin Panel":
    st.title("🔑 Admin Panel")

    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access Granted ✅")

        # Show all registrations
        st.subheader("📄 Registered Users")
        docs = db.collection(COLLECTION_NAME).stream()
        data = []
        for doc in docs:
            data.append(doc.to_dict())
        if data:
            st.table(data)
        else:
            st.info("No registrations found.")

        # Password re-confirmation for delete
        confirm_password = st.text_input("Re-enter Password to Confirm Delete", type="password")

        if confirm_password == ADMIN_PASSWORD:
            st.warning("⚠ This will permanently delete all registration data!")
            if st.button("🚨 ERASE ALL DATA", type="primary"):
                docs = db.collection(COLLECTION_NAME).stream()
                for doc in docs:
                    doc.reference.delete()
                st.success("All data erased successfully!")
        elif confirm_password:
            st.error("Passwords do not match ❌")

    elif password:
        st.error("Incorrect Password ❌")
