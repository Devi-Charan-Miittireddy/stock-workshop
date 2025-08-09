import streamlit as st
import pandas as pd
import os
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

def registration_page():
    st.title("📈 Stock Market Workshop Registration")
    with st.form(key='registration_form'):
        name = st.text_input("Full Name", max_chars=50)
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        college = st.text_input("College Name")
        branch = st.text_input("Branch")
        year = st.selectbox("Year", ["", "1st Year", "2nd Year", "3rd Year", "4th Year", "Other"])
        submit = st.form_submit_button("Register")

    if submit:
        if not all([name, email, phone, college, branch, year]):
            st.error("⚠ Please fill all fields before submitting.")
            return
        registration_data = {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "College": college,
            "Branch": branch,
            "Year": year,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_registration(registration_data)
        if send_confirmation_email(email, name):
            st.session_state["registered"] = True
            st.rerun()

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

            # Confirmation delete
            st.subheader("🗑 Delete All Registrations")
            confirm_text = st.text_input("Type DELETE to confirm deletion:", key="delete_confirm")
            if st.button("⚠ Confirm Delete", type="primary"):
                if confirm_text.strip().upper() == "DELETE":
                    if delete_all_registrations():
                        st.success("✅ All registration data has been deleted.")
                        st.rerun()  # Refresh page instantly
                    else:
                        st.info("No registration data found.")
                else:
                    st.error("❌ You must type DELETE to confirm.")

        else:
            st.info("No registrations yet.")

    elif password:
        st.error("Incorrect password")

def payment_page():
    st.title("💳 Payment Section")
    st.write("Please scan the QR code below to make your payment:")
    try:
        qr_image = Image.open("payment_qr.jpg")
        st.image(qr_image, caption="Scan to Pay", use_container_width=True)
    except FileNotFoundError:
        st.error("QR code image not found. Please upload 'payment_qr.jpg' to your repo.")

# -------- APP NAVIGATION --------
if "registered" not in st.session_state:
    st.session_state["registered"] = False

menu = st.sidebar.selectbox("Select Mode", ["Register", "Admin"])

if menu == "Register":
    if st.session_state["registered"]:
        payment_page()
    else:
        registration_page()
elif menu == "Admin":
    admin_page()
