import pandas as pd
import qrcode
import io
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Load API keys from config file
with open('../api_keys.json', 'r') as f:
    api_keys = json.load(f)

# Email config
smtp_server = api_keys['email_smtp_server']
port = api_keys['email_port']
sender_email = api_keys['email_sender']
password = api_keys['email_password']

qr_path = '../Assets/image/1749194440597.jpg'
logo_path = '../Assets/image/richmessage_1748246675760.jpg'

with open(qr_path, 'rb') as f:
    qr_data = f.read()
qr_cid = 'qrcode_image'

with open(logo_path, 'rb') as f:
    logo_data = f.read()
logo_cid = 'logo_image'

# Prepare recipient list as before (filtered DataFrame 'filtered')
'''df = pd.read_csv('clients.csv')
df['last_entry_date'] = pd.to_datetime(df['last_entry_date'])
latest = df.sort_values('last_entry_date').groupby('email', as_index=False).last()
today = datetime.now().date()
latest['days_since_last_entry'] = (today - latest['last_entry_date'].dt.date).dt.days
filtered = latest[latest['days_since_last_entry'] > 14]
'''

# Email content with embedded QR code and logo
subject = "Reminder: Please Retake the AMR Data Collection Survey"
html = f"""
<html>
<body>
<p>Dear Participant,</p>
<p>This is a friendly reminder to chat to AMI to retake our AMR Data Collection Survey if you have any symptoms.<br>
Scan the QR code below with your phone to access the survey:</p>
<p><img src="cid:{qr_cid}" alt="Survey QR Code" style="width:150px; height:150px;"></p>
<p>If you have any questions, please reply to this email. Thank you for your valuable contribution!</p>
<p><strong>C.Y</strong><br>
Mahidol Oxford Research Unit (MORU)<br>
Bangkok, Thailand</p><br>
<p><br><img src="cid:{logo_cid}" alt="Institution Logo" style="height:80px;"></p>
</body>
</html>
"""

filtered = ['chunyu.yang@ndm.ox.ac.uk']

# Send emails
server = smtplib.SMTP(smtp_server, port)
server.starttls()
server.login(sender_email, password)

# Read institution logo
with open(logo_path, 'rb') as f:
    logo_data = f.read()

for receiver_email in filtered:
    msg = MIMEMultipart('related')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg_alt = MIMEMultipart('alternative')
    msg.attach(msg_alt)
    msg_alt.attach(MIMEText(html, 'html'))

    # Attach QR image
    img_qr = MIMEImage(qr_data, _subtype="png")
    img_qr.add_header('Content-ID', f'<{qr_cid}>')
    img_qr.add_header('Content-Disposition', 'inline', filename="qrcode.png")
    msg.attach(img_qr)

    # Attach logo image
    img_logo = MIMEImage(logo_data)
    img_logo.add_header('Content-ID', f'<{logo_cid}>')
    img_logo.add_header('Content-Disposition', 'inline', filename="logo.png")
    msg.attach(img_logo)

    server.sendmail(sender_email, receiver_email, msg.as_string())

server.quit()
print("Email sent successfully!") 