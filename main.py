from flask import Flask, render_template, request, flash
from forms.RegistrationForm import RegistrationForm
from forms.AttandanceForm import AttendanceForm
from werkzeug.utils import secure_filename
from facedb import FaceDB
from dotenv import load_dotenv
import psycopg2.extras
import os
import psycopg2
import uuid
import sqlite3

load_dotenv()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app = Flask(__name__, static_folder='public')
app.config['SECRET_KEY'] = 'secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

os.environ['PINECONE_API_KEY'] = os.getenv('PINECONE_API_KEY')

conn = sqlite3.connect("database.sqlite3", check_same_thread=False)
conn.row_factory = dict_factory
cur = conn.cursor()
faceDB = FaceDB(
    metric='euclidean',
    database_backend='pinecone',
    pinecone_settings={
        "index_name": 'absensi-ai-lite',
    },
    embedding_dim=128,
    module='face_recognition',
)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    errors = []
    if request.method == 'POST':
        if not form.validate():
            errors = form.errors
        else:

            print(request.files)

            # Generate a random UUID
            face_id = str(uuid.uuid4())

            # save the image to the uploads folder

            file = form.face.data
            filename = face_id + "." + secure_filename(file.filename).split('.')[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # generate face encoding and add to pinecone
            faceDB.add(form.name.data, img=file_path, id=face_id, email=form.email.data)

            os.remove(file_path)

            # Insert the data into the database
            cur.execute("""
            INSERT INTO users (face_id, name, email, face_image)
            VALUES (?, ?, ?, ?)
            """, (face_id, form.name.data, form.email.data, file_path))
            conn.commit()

            flash('Successfully registered!')
            return render_template('index.html')

    return render_template('registrasi.html', form=form, errors=errors)


@app.route('/attendance-history', methods=['GET'])
def attendance_history():
    cur.execute(""" 
        SELECT u.name, u.email, u.face_id, a.created_at
        FROM users u
        JOIN attendances a ON u.id = a.user_id
        ORDER BY a.created_at DESC
    """)
    attendances = cur.fetchall()
    print(attendances)
    return render_template('history.html', attendances=attendances)


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    form = AttendanceForm()
    errors = []
    if request.method == 'POST':

        try:
            if not form.validate():
                errors = form.errors
                print(form.errors)
            else:

                # save the image to the tmp uploads folder
                file = form.face.data

                if not file:
                    flash('No file selected!', 'error')
                    return render_template('attendances.html')

                filename = str(uuid.uuid4()) + "." + secure_filename(file.filename).split('.')[1]
                file_path = os.path.join(app.config['UPLOAD_FOLDER'] + "/tmp", filename)
                file.save(file_path)

                # recognize the face
                result = faceDB.recognize(img=file_path)

                # delete the file
                os.remove(file_path)

                if result is None:
                    flash('Face not recognized!', 'error')
                    return render_template('attendances.html')

                print(result)
                cur.execute("SELECT id, name FROM users WHERE face_id = ?", (result['id'],))
                user = cur.fetchone()
                print(user)

                if user is None:
                    flash('User not found!')
                    return render_template('index.html')

                cur.execute("""
                INSERT INTO attendances (user_id)
                VALUES (?)
                """, (user['id'],))
                conn.commit()

                flash('Successfully attended!, hello ' + user['name'])

        except:
            flash("Error while recognizing face!", 'error')

    return render_template('attendances.html', form=form, errors=errors)


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    if not os.path.exists(app.config['UPLOAD_FOLDER'] + "/tmp"):
        os.makedirs(app.config['UPLOAD_FOLDER'] + "/tmp")
    app.run(debug=True)
