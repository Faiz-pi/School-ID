from flask import Flask, render_template, request
from flask import Flask, render_template, request
import os
import gspread

from oauth2client.service_account import ServiceAccountCredentials

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    scope
)

client = gspread.authorize(creds)

sheet = client.open("Student Database").sheet1


drive_scopes = ['https://www.googleapis.com/auth/drive']

drive_creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=drive_scopes
)

drive_service = build(
    'drive',
    'v3',
    credentials=drive_creds
)

@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':

        student_name = request.form['student_name']
        student_class = request.form['class']
        section = request.form['section']
        dob = request.form['dob']
        father_name = request.form['father_name']
        mother_name = request.form['mother_name']
        mobile = request.form['mobile']
        address = request.form['address']

        photo = request.files['photo']

        photo_path = os.path.join(
            UPLOAD_FOLDER,
            photo.filename
        )

        photo.save(photo_path)

        file_metadata = {
            'name': photo.filename
        }

        media = MediaFileUpload(photo_path)

        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = uploaded_file.get('id')

        drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()

        photo_link = f"https://drive.google.com/uc?id={file_id}"

        sheet.append_row([
            student_name,
            student_class,
            section,
            dob,
            father_name,
            mother_name,
            mobile,
            address,
            photo_link
        ])

        return render_template(
            'form.html',
            success=True
            )

    return render_template('form.html')


if __name__ == '__main__':
    app.run()