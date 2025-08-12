# get_maersk.py
import os
import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# --- CONFIG ---
TICKER = "MAERSK-A.CO"
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
EMAIL_TO = os.environ["EMAIL_TO"]
CSV_FILENAME = "maersk_intraday.csv"


# --- GET DATA ---
stock = yf.Ticker(TICKER)
df = stock.history(period="1d", interval="1m")
df.to_csv(CSV_FILENAME)

# --- EMAIL SETUP ---
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_TO
msg['Subject'] = f"Maersk A Intraday Data - {datetime.now().date()}"

body = "Attached is today's intraday Maersk A stock price data."
msg.attach(MIMEText(body, 'plain'))

with open(CSV_FILENAME, "rb") as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename= {CSV_FILENAME}')
    msg.attach(part)

# --- SEND EMAIL ---
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASS)
server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
server.quit()
