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

# Safe defaults if secrets not set (useful for local run)
ADMIN_PASSWORD = st.secrets.get("app", {}).get("admin_password", "admin123")
EMAIL_ADDRESS = st.secrets.get("email", {}).get("address", "")
EMAIL_PASSWORD = st.secrets.get("email", {}).get("password", "")

WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"
QR_IMAGE_PATH = "payment_qr.jpg"  # Must be in repo

# -------- FUNCTIONS --------
def send_confirmation_email(to_email, name):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        st.error("Email credentials not configured in secrets.")
        return False

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
        return len(pd.read_csv(CSV_FILE))
    return 0

def delete_all_registrations():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)
        return True
    return False

# -------- PAGES --------
def registration_page():
    st.title("📈 Stock Market Workshop Registration")
    st.warning("⚠ Once you submit the form, your details cannot be changed. Please check carefully before registering.")

    with st.form(key='registration_form'):
        name = st.text_input("Full Name", max_chars=50)
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        college = st.text_input("College Name")
        branch = st.selectbox("Branch", ["", "CSE", "ECE", "EEE", "MECH", "CIVIL", "IT", "CSD", "CSM", "CHEM"])
        year = st.selectbox("Year", ["", "1st Year", "2nd Year", "3rd Year", "4th Year"])
        submit = st.form_submit_button("Register")

    if submit:
        if not all([name, email, phone, college, branch, year]):
            st.error("⚠ Please fill all fields before submitting.")
            return

        save_registration({
            "Name": name,
            "Email": email,
            "Phone": phone,
            "College": college,
            "Branch": branch,
            "Year": year,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        st.session_state["registered"] = True
        st.session_state["user_email"] = email
        st.session_state["user_name"] = name
        st.experimental_rerun()

def admin_page():
    st.title("🔑 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success(f"✅ Total Registered Participants: {get_registration_count()}")

        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            st.dataframe(df)

            st.download_button(
                label="📥 Download Registrations CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="registrations.csv",
                mime="text/csv"
            )

            st.subheader("🗑 Delete All Registrations")
            confirm_password = st.text_input("Re-enter Admin Password to Confirm Deletion:", type="password")
            if st.button("⚠ Confirm Delete"):
                if confirm_password == ADMIN_PASSWORD and delete_all_registrations():
                    st.success("✅ All registration data deleted.")
                    st.experimental_rerun()
                else:
                    st.error("❌ Incorrect password or no data found.")
        else:
            st.info("No registrations yet.")
    elif password:
        st.error("Incorrect password")

def payment_page():
    st.title("💳 Payment Section")
    st.write("Please scan the QR code below to make your payment:")

    if os.path.exists(QR_IMAGE_PATH):
        st.image(QR_IMAGE_PATH, caption="Scan to Pay", width=300)
    else:
        st.error(f"QR code image '{QR_IMAGE_PATH}' not found in repo.")

    transaction_id = st.text_input("Enter UPI Transaction ID (12 digits)")

    if not st.session_state.get("payment_confirmed", False):
        uploaded_file = st.file_uploader("Upload payment screenshot", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None and st.button("Confirm Payment"):
            if len(transaction_id) != 12 or not transaction_id.isdigit():
                st.error("⚠ Please enter a valid 12-digit numeric UPI transaction ID.")
            else:
                st.session_state["payment_confirmed"] = True
                if send_confirmation_email(st.session_state["user_email"], st.session_state["user_name"]):
                    st.success("📧 Confirmation email sent!")
                st.session_state["confirmation_page"] = True
                st.experimental_rerun()
    else:
        st.success("✅ Payment confirmed.")
        st.markdown(f"[💬 Join our WhatsApp Group]({WHATSAPP_LINK})", unsafe_allow_html=True)

def confirmation_page():
    st.title("✅ Registration Successful")
    st.success("Registration successful! Confirmation mail sent to your email.")
    st.markdown(f"[💬 Join our WhatsApp Group]({WHATSAPP_LINK})", unsafe_allow_html=True)

# -------- APP NAVIGATION --------
if "registered" not in st.session_state:
    st.session_state["registered"] = False
if "payment_confirmed" not in st.session_state:
    st.session_state["payment_confirmed"] = False
if "confirmation_page" not in st.session_state:
    st.session_state["confirmation_page"] = False

menu = st.sidebar.selectbox("Select Mode", ["Register", "Admin"])

if menu == "Register":
    if st.session_state["confirmation_page"]:
        confirmation_page()
    elif st.session_state["registered"]:
        payment_page()
    else:
        registration_page()
elif menu == "Admin":
    admin_page()
