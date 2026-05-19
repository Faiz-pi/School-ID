from flask import Flask, render_template, request
from flask import Flask, render_template, request
import os
import gspread

from oauth2client.service_account import ServiceAccountCredentials

import cloudinary
import cloudinary.uploader

app = Flask(__name__)
cloudinary.config(
    cloud_name='dbty6ldp3',
    api_key='157723142692988',
    api_secret='7gRLOXiddFshnO8QxZMWqDtqV54'
)

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

        upload_result = cloudinary.uploader.upload(
            photo_path
        )

        photo_link = upload_result['secure_url']

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