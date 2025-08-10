import streamlit as st
import pandas as pd
import os
import time
import random
import string
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
def generate_registration_id():
    """Generate a unique 8-character registration ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def send_confirmation_email(to_email, name, registration_id):
    subject = "Workshop Registration Confirmation"
    body = f"""
Hi {name},

Thank you for registering for the Stock Market Workshop.
We have received your registration successfully.

Your Registration ID is: {registration_id}

Please keep this ID safe for future reference.

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
        existing_df = pd.read_csv(CSV_FILE)
        # Ensure RegistrationID column exists
        if "RegistrationID" not in existing_df.columns:
            existing_df["RegistrationID"] = ""
        df = pd.concat([existing_df, df], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
    else:
        if "RegistrationID" not in df.columns:
            df["RegistrationID"] = ""
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
def registration_page():
    st.title("📈 Stock Market Workshop Registration")
    st.markdown(
        "<div style='background-color:#ffeeba; padding:10px; border-radius:5px; color:#856404; font-weight:bold;'>"
        "⚠ Once you submit the form, your details cannot be changed. Please check carefully before registering."
        "</div>",
        unsafe_allow_html=True
    )

    with st.form(key='registration_form'):
        name = st.text_input("Full Name", max_chars=50)
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        college = st.text_input("College Name")
        branch = st.selectbox("Branch", ["", "CSE", "ECE", "EEE", "MECH", "CIVIL", "IT", "CSD", "CSM", "CHEM"])
        year = st.selectbox("Year", ["", "1st Year", "2nd Year", "3rd Year", "4th Year"])
        submit = st.form_submit_button("Submit")

    if submit:
        if not all([name, email, phone, college, branch, year]):
            st.error("⚠ Please fill all fields before submitting.")
            return

        # ✅ Duplicate email prevention
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if "Email" in df.columns and email.strip().lower() in df['Email'].str.lower().values:
                st.error("⚠ This email is already registered. Please use a different email.")
                return

        registration_data = {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "College": college,
            "Branch": branch,
            "Year": year,
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "RegistrationID": ""  # Will be filled after payment
        }
        save_registration(registration_data)
        st.success("✅ Submission successful... You are being directed to payment section")
        time.sleep(3)
        st.session_state["registered"] = True
        st.session_state["user_email"] = email
        st.session_state["user_name"] = name
        st.session_state["payment_confirmed"] = False
        st.session_state["show_proceed"] = False
        st.session_state["thank_you"] = False
        st.rerun()

def admin_page():
    st.title("🔑 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success(f"✅ Total Registered Participants: {get_registration_count()}")

        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if "RegistrationID" not in df.columns:
                df["RegistrationID"] = ""
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
            if st.button("Proceed"):
                if not (transaction_id.isdigit() and len(transaction_id) == 12):
                    st.error("⚠ Please enter a valid 12-digit numeric UPI Transaction Id before proceeding.")
                else:
                    if "user_email" in st.session_state and "user_name" in st.session_state:
                        registration_id = generate_registration_id()

                        if os.path.exists(CSV_FILE):
                            df = pd.read_csv(CSV_FILE)
                            if "RegistrationID" not in df.columns:
                                df["RegistrationID"] = ""
                            df.loc[df['Email'].str.lower() == st.session_state["user_email"].lower(), 'RegistrationID'] = registration_id
                            df.to_csv(CSV_FILE, index=False)

                        sent = send_confirmation_email(
                            st.session_state["user_email"], 
                            st.session_state["user_name"], 
                            registration_id
                        )
                        if sent:
                            st.session_state["thank_you"] = True
                        else:
                            st.error("❌ Failed to send registration email.")

                        del st.session_state["user_email"]
                        del st.session_state["user_name"]

                    st.session_state["payment_confirmed"] = True
                    st.rerun()
    else:
        st.info("You have already completed payment and registration.")

def thank_you_page():
    st.markdown(
        "<h1 style='text-align:center; font-size:60px; color:green;'>🎉 THANK YOU! 🎉</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='text-align:center;'>Registration Successful... Details have been sent to your mail.</h3>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="text-align:center; margin-top:30px;">
            <a href="{WHATSAPP_LINK}" target="_blank" 
               style="background-color:#25D366; color:white; padding:15px 30px; 
                      text-decoration:none; font-size:20px; border-radius:8px; 
                      display:inline-block;">
                📲 Join WhatsApp Group
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------- APP NAVIGATION --------
if "registered" not in st.session_state:
    st.session_state["registered"] = False
if "payment_confirmed" not in st.session_state:
    st.session_state["payment_confirmed"] = False
if "show_proceed" not in st.session_state:
    st.session_state["show_proceed"] = False
if "thank_you" not in st.session_state:
    st.session_state["thank_you"] = False

menu = st.sidebar.selectbox("Select Mode", ["Register", "Admin"])

if menu == "Register":
    if st.session_state["thank_you"]:
        thank_you_page()
    elif st.session_state["registered"]:
        payment_page()
    else:
        registration_page()
elif menu == "Admin":
    admin_page()
