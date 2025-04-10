from flask import Flask, request
import requests
from PIL import Image
from io import BytesIO
import pytesseract 
import gspread 
from oauth2client.service_account import ServiceAccountCredentials 

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.form  # Ambil data form yang dikirim oleh Twilio
    
    # Cek apakah ada media dalam pesan 
    if 'MediaContentType0' in data:  # Pastikan ada konten media 
        media_url = data['MediaUrl0']  # Ambil URL media pertama
        
        text_result = extract_text_from_image(media_url)  
        
        if text_result:  
            update_sheet(text_result)  # Kirim hasil ke Google Sheets
            
        return "Success", 200
    
    return "No Media Found", 400

def extract_text_from_image(media_url):
    response = requests.get(media_url)
    
    if response.status_code == 200:
        try:
            img = Image.open(BytesIO(response.content))
            text = pytesseract.image_to_string(img)
            return text.strip()  # Kembalikan teks tanpa spasi tambahan 
        except Exception as e:
            print(f"Error opening image: {e}")
            return None
    
    print(f"Failed to retrieve image, status code: {response.status_code}")
    return None

def setup_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    
    creds = ServiceAccountCredentials.from_json_keyfile_name('path_to_your_credentials.json', scope)  
   
   client = gspread.authorize(creds)  
   sheet = client.open("Your Sheet Name").sheet1  
    
   return sheet

def update_sheet(text):
   sheet = setup_google_sheets()
   sheet.append_row([text])  

if __name__ == '__main__':
    app.run(debug=True)
