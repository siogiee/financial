
from flask import Flask, request
import requests
from PIL import Image
from io import BytesIO
import pytesseract
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.form
    media_url = data.get("MediaUrl0")
    from_number = data.get("From")

    if media_url:
        img_response = requests.get(media_url)
        img = Image.open(BytesIO(img_response.content))

        text = pytesseract.image_to_string(img)
        parsed = parse_receipt_text(text)
        save_to_sheet(parsed)

        return f"Tersimpan:\n{parsed}"

    return "Gambar tidak ditemukan."

def parse_receipt_text(text):
    lines = text.split("\n")
    total = ""
    for line in lines:
        if 'total' in line.lower():
            total = line
            break
    return text + "\nTotal: " + total

def save_to_sheet(text):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("Catatan Keuangan").sheet1
    sheet.append_row([text])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
