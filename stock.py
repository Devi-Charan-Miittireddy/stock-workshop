import streamlit as st
import pandas as pd
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# -------- CONFIGURATION --------
CSV_FILE = "registrations.csv"
ADMIN_PASSWORD = "admin123"  # Change this to your real admin password
EMAIL_ADDRESS = "your_email@gmail.com"  # Sender email
EMAIL_PASSWORD = "your_email_password"  # Sender email password
WHATSAPP_LINK = "https://chat.whatsapp.com/yourgroup"

# -------- INITIAL SETUP --------
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Name", "Email", "Phone", "Registered_At", "Payment_Status"])
    df.to_csv(CSV_FILE, index=False)

# -------- EMAIL FUNCTION --------
def send_email(to_email, name):
    subject = "Registration Confirmation"
    body = f"Hello {name},\n\nYour registration and payment have been successfully completed.\n\nWelcome!\n\nRegards,\nTeam"
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email sending failed: {e}")
        return False

# -------- REGISTRATION PAGE --------
def registration_page():
    st.header("Registration Form")
    st.markdown(
        "<div style='background-color:orange; padding:10px; border-radius:5px; color:black; font-weight:bold;'>⚠️ Once you submit the form, your details cannot be changed. Please check carefully before submitting.</div>",
        unsafe_allow_html=True
    )
    st.write("")

    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")

        submitted = st.form_submit_button("Register")

        if submitted:
            if not name or not email or not phone:
                st.error("Please fill all fields before submitting.")
            else:
                df = pd.read_csv(CSV_FILE)
                new_data = pd.DataFrame(
                    [[name, email, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Pending"]],
                    columns=["Name", "Email", "Phone", "Registered_At", "Payment_Status"]
                )
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)

                st.success("✅ Registration successful!")
                st.info("⏳ You are being directed to the Payment section...")
                time.sleep(2)
                st.session_state.page = "Payment"

# -------- PAYMENT PAGE --------
def payment_page():
    st.header("Payment Section")
    st.write("Please complete your payment using the provided QR code or link below.")

    st.markdown(f"[Join our WhatsApp Group for payment confirmation]({WHATSAPP_LINK})")

    with st.form("payment_form"):
        email = st.text_input("Enter your registered email to confirm payment")
        payment_done = st.checkbox("I have completed the payment")

        submitted = st.form_submit_button("Confirm Payment")

        if submitted:
            if not email:
                st.error("Please enter your email.")
            else:
                df = pd.read_csv(CSV_FILE)
                if email in df["Email"].values:
                    if payment_done:
                        df.loc[df["Email"] == email, "Payment_Status"] = "Paid"
                        df.to_csv(CSV_FILE, index=False)

                        user_name = df.loc[df["Email"] == email, "Name"].values[0]
                        if send_email(email, user_name):
                            st.success("✅ Payment confirmed! Confirmation email sent.")
                    else:
                        st.warning("Please tick the checkbox after making payment.")
                else:
                    st.error("Email not found in our records.")

# -------- ADMIN PAGE --------
def admin_page():
    st.header("Admin Panel")
    st.subheader("View All Registrations")

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)

    st.subheader("Erase All Data (Password Protected)")
    password_input = st.text_input("Enter Admin Password to delete all data", type="password")
    if st.button("Delete All Data"):
        if password_input == ADMIN_PASSWORD:
            df = pd.DataFrame(columns=["Name", "Email", "Phone", "Registered_At", "Payment_Status"])
            df.to_csv(CSV_FILE, index=False)
            st.success("✅ All data erased successfully.")
        else:
            st.error("Incorrect password. Access denied.")

# -------- PAGE NAVIGATION --------
if "page" not in st.session_state:
    st.session_state.page = "Registration"

menu = st.sidebar.radio("Navigation", ["Registration", "Payment", "Admin"])

if menu == "Registration":
    st.session_state.page = "Registration"
    registration_page()
elif menu == "Payment":
    st.session_state.page = "Payment"
    payment_page()
elif menu == "Admin":
    admin_page()
