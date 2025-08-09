import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import uuid

# --------- CONFIGURATION ---------
WHATSAPP_LINK = "https://chat.whatsapp.com/KpkyyyevxqmFOnkaZUsTo2"

# Load secrets
EMAIL_ADDRESS = st.secrets["email"]["address"]
EMAIL_PASSWORD = st.secrets["email"]["password"]
FIREBASE_CONFIG = st.secrets["firebase"]

# --------- FIREBASE SETUP ---------
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CONFIG)
        firebase_admin.initialize_app(cred, {
            "storageBucket": f"{FIREBASE_CONFIG['project_id']}.appspot.com"
        })
    db = firestore.client()
    bucket = storage.bucket()
    registrations_ref = db.collection("registrations")
except Exception as e:
    st.error(f"Failed to initialize Firebase: {e}")
    st.stop()

# --------- HELPER FUNCTIONS ---------
def is_valid_email(email):
    """Check if email is in valid format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def email_exists(email):
    """Check if the email already exists in Firestore."""
    docs = registrations_ref.where("Email", "==", email).stream()
    return any(docs)

def send_confirmation_email(to_email, name):
    """Send confirmation email via Gmail SMTP."""
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
    """Save registration to Firestore."""
    try:
        registrations_ref.add(data)
        return True
    except Exception as e:
        st.error(f"Firestore error: {e}")
        return False

def get_registration_count():
    """Get the total number of registrations."""
    try:
        docs = registrations_ref.stream()
        return len(list(docs))
    except Exception as e:
        st.error(f"Error getting registration count: {e}")
        return 0

def upload_payment_screenshot(file):
    """Upload screenshot to Firebase Storage and return public URL."""
    try:
        file_id = str(uuid.uuid4())
        blob = bucket.blob(f"payment_screenshots/{file_id}_{file.name}")
        blob.upload_from_file(file, content_type=file.type)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        st.error(f"Error uploading screenshot: {e}")
        return None

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
    uploaded_file = st.file_uploader("Upload your payment screenshot (PNG/JPG)", type=["png", "jpg", "jpeg"])
    submit = st.form_submit_button("Register")

if submit:
    if not (name and email and phone and college and branch and year and uploaded_file):
        st.error("Please fill all fields and upload payment screenshot.")
    elif not is_valid_email(email):
        st.error("Please enter a valid email address.")
    elif email_exists(email):
        st.warning("You have already registered with this email.")
    else:
        # Upload screenshot
        screenshot_url = upload_payment_screenshot(uploaded_file)
        if screenshot_url:
            # Save data to Firestore
            registration_data = {
                "Name": name,
                "Email": email,
                "Phone": phone,
                "College": college,
                "Branch": branch,
                "Year": year,
                "PaymentScreenshot": screenshot_url,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            saved = save_registration(registration_data)
            if saved:
                email_sent = send_confirmation_email(email, name)
                if email_sent:
                    st.success("✅ Registration successful! A confirmation email has been sent.")
                else:
                    st.warning("✅ Registered, but failed to send confirmation email.")
                st.markdown(f"**Join the WhatsApp group here:** [Click to Join]({WHATSAPP_LINK})")
            else:
                st.error("❌ Failed to save your registration. Please try again later.")

# --------- Registration Count ---------
st.markdown("---")
st.markdown(f"### Total Registered Participants: {get_registration_count()}")
