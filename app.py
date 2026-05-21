from flask import Flask, render_template, request
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/idcards', exist_ok=True)

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
        os.remove(photo_path)
        all_records = sheet.get_all_records()

        student_id = len(all_records) + 1
        sheet.append_row([
            student_id,
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

        idcard_link = f"https://school-id-1.onrender.com/id/{student_id}"

        sheet.update_cell(
            len(all_records) + 2,
            11,
            idcard_link
        )

        return render_template(
            'form.html',
            success=True
            )

    return render_template('form.html')

@app.route('/id/<int:student_id>')
def view_id(student_id):

    all_records = sheet.get_all_records()

    student = next(
        (
            item for item in all_records
            if int(item["ID"]) == student_id
        ),
        None
    )

    if not student:
        return "Student not found"

    return render_template(
        'idcard.html',
        student=student
    )

if __name__ == '__main__':
    app.run()