import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --------- CONFIGURATION ---------
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"

EMAIL_ADDRESS = "m.pavankumar679@gmail.com"
EMAIL_PASSWORD = "pavankumar123"

# --------- FIREBASE SETUP ---------
if not firebase_admin._apps:
    cred = credentials.Certificate("stockmarket-ws-be7ae-firebase-adminsdk-fbsvc-714919cf7a.json")  # path to your key
    firebase_admin.initialize_app(cred)

db = firestore.client()
registrations_ref = db.collection("registrations")

# --------- FUNCTIONS ---------
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
        st.error(f"Error sending email: {e}")
        return False

def save_registration(data: dict):
    registrations_ref.add(data)

def get_registration_count():
    docs = registrations_ref.stream()
    return len(list(docs))

# --------- STREAMLIT UI ---------
st.title("📈 Stock Market Workshop Registration")
st.markdown("Fill the form below to register for the workshop.")

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
            st.success("Registration successful! A confirmation email has been sent.")
        else:
            st.warning("Registered, but failed to send confirmation email.")

st.markdown("---")
st.markdown(f"### Total Registered Participants: {get_registration_count()}")

st.markdown("### Upload Payment Screenshot")
uploaded_file = st.file_uploader("Upload your payment screenshot (PNG/JPG)")

if uploaded_file is not None:
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    save_path = os.path.join("screenshots", uploaded_file.name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Payment screenshot uploaded successfully!")
    st.markdown(f"**Join the WhatsApp group here:** [Click to Join]({WHATSAPP_LINK})")
