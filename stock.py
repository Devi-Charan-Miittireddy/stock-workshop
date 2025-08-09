import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --------- CONFIGURATION ---------
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"

# Load secrets for email (set these in Streamlit Cloud -> Settings -> Secrets)
EMAIL_ADDRESS = st.secrets["email"]["address"]
EMAIL_PASSWORD = st.secrets["email"]["password"]

# --------- FIREBASE SETUP ---------
try:
    if not firebase_admin._apps:
        firebase_key = st.secrets["firebase"]  # Load from secrets
        cred = credentials.Certificate(firebase_key)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    registrations_ref = db.collection("registrations")
except Exception as e:
    st.error(f"Failed to initialize Firebase: {e}")
    st.stop()

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
        st.error(f"Error sending confirmation email: {e}")
        return False

def save_registration(data: dict):
    try:
        registrations_ref.add(data)
        return True
    except Exception as e:
        st.error(f"Firestore error: {e}")
        return False

def get_registration_count():
    try:
        docs = registrations_ref.stream()
        return len(list(docs))
    except Exception as e:
        st.error(f"Error getting registration count: {e}")
        return 0

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
        saved = save_registration(registration_data)
        if saved:
            email_sent = send_confirmation_email(email, name)
            if email_sent:
                st.success("✅ Registration successful! A confirmation email has been sent.")
                st.markdown(f"**Join the WhatsApp group here:** [Click to Join]({WHATSAPP_LINK})")
            else:
                st.warning("✅ Registered, but failed to send confirmation email.")
        else:
            st.error("❌ Failed to save your registration. Please try again later.")

# --------- Registration Count ---------
st.markdown("---")
st.markdown(f"### Total Registered Participants: {get_registration_count()}")
