import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------- CONFIGURATION ----------------
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"
CSV_FILE = "registrations.csv"
ADMIN_PASSWORD = "admin123"  # Change this to your real admin password
EMAIL_ADDRESS = "your_email@example.com"  # Your email
EMAIL_PASSWORD = "your_password"  # Your email password

# ---------------- EMAIL FUNCTION ----------------
def send_email(to_email, name):
    try:
        subject = "Workshop Registration Confirmation"
        body = f"""
Hello {name},

Thank you for registering for our Stock Market Workshop.
We will contact you with further details soon.

WhatsApp Group Link: {WHATSAPP_LINK}

Best regards,
Workshop Team
"""
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email sending failed: {e}")
        return False

# ---------------- SAVE TO CSV ----------------
def save_to_csv(data):
    df = pd.DataFrame([data])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)

# ---------------- DELETE ALL DATA ----------------
def delete_all_data(password):
    if password == ADMIN_PASSWORD:
        if os.path.exists(CSV_FILE):
            os.remove(CSV_FILE)
            st.success("All registration data has been deleted.")
        else:
            st.warning("No registration data found.")
    else:
        st.error("Incorrect admin password.")

# ---------------- REGISTRATION PAGE ----------------
def registration_page():
    st.header("📌 Stock Market Workshop Registration")
    st.markdown("⚠ **Once you submit the form, your details cannot be changed. Please check carefully before registering.**")

    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        submit_button = st.form_submit_button("Register")

    if submit_button:
        if not name or not email or not phone:
            st.error("Please fill in all fields.")
        else:
            data = {
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Registration Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_to_csv(data)

            if send_email(email, name):
                st.success("✅ Registration successful! Confirmation email sent.")
            else:
                st.warning("Registered, but confirmation email could not be sent.")

            st.info(f"📢 Join our WhatsApp Group: [Click Here]({WHATSAPP_LINK})")

# ---------------- ADMIN PAGE ----------------
def admin_page():
    st.header("🔐 Admin Panel")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.subheader("📋 All Registrations")
        st.dataframe(df)
    else:
        st.info("No registration data found.")

    st.subheader("❌ Delete All Data")
    password_input = st.text_input("Enter Admin Password to Delete All Data", type="password")
    if st.button("Delete Data"):
        delete_all_data(password_input)

# ---------------- MAIN APP ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Registration", "Admin"])

if page == "Registration":
    registration_page()
elif page == "Admin":
    admin_page()
