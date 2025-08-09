import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------- CONFIG --------
CSV_FILE = "registrations.csv"
ADMIN_PASSWORD = "admin123"  # Change this to your own admin password
EMAIL_ADDRESS = "m.pavankumar679@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"  # App password, not normal password
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

# -------- APP MODE --------
menu = st.sidebar.selectbox("Select Mode", ["Register", "Admin"])

if menu == "Register":
    st.title("📈 Stock Market Workshop Registration")
    with st.form(key='registration_form'):
        name = st.text_input("Full Name", max_chars=50)
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        college = st.text_input("College Name")
        branch = st.text_input("Branch")
        year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Other"])
        submit = st.form_submit_button("Register")

    if submit:
        if not (name and email and phone and college and branch and year):
            st.error("Please fill all fields before submitting.")
        else:
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
            email_sent = send_confirmation_email(email, name)
            if email_sent:
                st.success("✅ Registration successful! A confirmation email has been sent.")
            else:
                st.warning("✅ Registered, but failed to send confirmation email.")
            st.markdown(f"**Join the WhatsApp group here:** [Click to Join]({WHATSAPP_LINK})")

    st.markdown("---")
    st.markdown(f"### Total Registered Participants: {get_registration_count()}")

elif menu == "Admin":
    st.title("🔑 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            st.dataframe(df)

            # Download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Registrations CSV",
                data=csv,
                file_name="registrations.csv",
                mime="text/csv"
            )
        else:
            st.info("No registrations yet.")
    elif password:
        st.error("Incorrect password")
