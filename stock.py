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
EMAIL_ADDRESS = "charancherryh1438@gmail.com"
EMAIL_PASSWORD = "xsab exlq lool uuyk"  # Gmail App Password

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

# -------- STATE --------
if "page" not in st.session_state:
    st.session_state.page = "register"

# -------- APP LOGIC --------
if st.session_state.page == "register":
    menu = st.sidebar.selectbox("Select Mode", ["Register", "Admin"])

    if menu == "Register":
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
            if not name or not email or not phone or not college or not branch or not year:
                st.warning("⚠ Please fill all fields before submitting.")
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
                    st.session_state.page = "payment"  # Go to payment page
                    st.rerun()
                else:
                    st.warning("✅ Registered, but failed to send confirmation email.")

    elif menu == "Admin":
        st.title("🔑 Admin Panel")
        password = st.text_input("Enter Admin Password", type="password")

        if password == ADMIN_PASSWORD:
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
                st.dataframe(df)

                st.markdown(f"### Total Registered Participants: {get_registration_count()}")

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

elif st.session_state.page == "payment":
    st.title("💳 Payment Section")
    st.write("Please complete your payment to confirm your registration.")

    # Example: QR code or payment instructions
   import streamlit as st
from PIL import Image

def payment_page():
    st.title("💳 Payment Section")
    st.markdown("Please complete your payment using the QR code below:")

    # Load and display the QR code image
    qr_image = Image.open("4929e0c6-2246-4f5a-a56e-e55f987c80ec.jpg")
    st.image(qr_image, caption="Scan to Pay using PhonePe", use_container_width=True)

    st.markdown("Once payment is completed, please send the screenshot to the admin.")

# Inside your registration submit success block:
if email_sent:
    st.success("✅ Registration successful! A confirmation email has been sent.")
    st.markdown("---")
    payment_page()

