import os
import yfinance as yf
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta

# --- CONFIG ---
TICKERS = ["MAERSK-A.CO", "MAERSK-B.CO"]
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
EMAIL_TO = os.environ["EMAIL_TO"]
CSV_FILENAME = "maersk_daily.csv"

# --- SET DATE MANUALLY ---
date_str = "2025-08-21"   # change this to the missed day
start_date = date_str
end_date = (datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")

# --- GET DATA FOR BOTH TICKERS ---
all_data = []
for ticker in TICKERS:
    stock = yf.Ticker(ticker)
    df = stock.history(start=start_date, end=end_date, interval="1m")
    df.reset_index(inplace=True)
    df["Ticker"] = ticker
    all_data.append(df)

# Combine all data
final_df = pd.concat(all_data)

# Sort by Ticker first, then Date
final_df.sort_values(by=["Ticker", "Date"], inplace=True)

# Save to CSV
final_df.to_csv(CSV_FILENAME, index=False)

# --- EMAIL SETUP ---
msg = MIMEMultipart()
msg['From'] = EMAIL_USER
msg['To'] = EMAIL_TO
msg['Subject'] = f"Maersk A & B Daily Data - {date_str}"

body = f"Attached is the daily data for Maersk A and B stocks on {date_str}."
msg.attach(MIMEText(body, 'plain'))

with open(CSV_FILENAME, "rb") as attachment:
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={CSV_FILENAME}')
    msg.attach(part)

# --- SEND EMAIL ---
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(EMAIL_USER, EMAIL_PASS)
server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
server.quit()
