
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
    from twilio.twiml.messaging_response import MessagingResponse

    num_media = int(request.form.get("NumMedia", 0))
    resp = MessagingResponse()

    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        text = extract_text_from_image(media_url)
        append_to_sheet(text)
        resp.message(f"Teks dari gambar berhasil diekstrak dan disimpan!\n\n{text[:300]}...")
    else:
        resp.message("Silakan kirim foto struk belanja untuk diproses.")

    return str(resp)

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

def extract_text_from_image(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text

def parse_receipt_text(text):
    lines = text.split("\n")
    total = ""
    for line in lines:
        if 'total' in line.lower():
            total = line
            break
    return text + "\nTotal: " + total

def append_to_sheet(text):
    sheet_id = '1Cgjj8fPBsBWVU3ICSOYVfbeKn4WPLZZnYh7JqZxd5Yk'
    range_name = 'Catatan Keuangan'
    values = [[text]]
    body = {"values": values}
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="RAW",
        body=body
    ).execute()

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
