import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
import secrets
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# Define flask variables
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
website_url = "http://localhost:5000/"

# DB initialisation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


# DB models
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String)
    report_id = db.Column(db.Integer)

    def image_url(self):
        return website_url + "static/uploads/" + self.image_filename


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason_for_report = db.Column(db.String)
    location_address = db.Column(db.String)
    location_postcode = db.Column(db.String)
    location_lat = db.Column(db.Integer)
    location_long = db.Column(db.Integer)
    reporter_email = db.Column(db.String)
    business_name = db.Column(db.String)
    council_name = db.Column(db.String)
    report_unique_id = db.Column(db.String)

    def report_unique_url(self):
        return website_url + "report/" + self.report_unique_id


# Helpers

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Endpoints

@app.route('/upload_file/to/<report_id>', methods=['POST'])
def upload_file(report_id = None):

    # check if report ID provided
    if report_id is None:
        flash ("No associated report ID")
        return redirect(request.url)

    # check if the post request has a file
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']

    # check if the post has a filename (it not probably indicates something is wrong)
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    # if all good then crack on
    if file and allowed_file(file.filename):
        file_extension = Path(file.filename).suffix
        filename = secrets.token_hex(16) + file_extension
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # insert code here to create image record
        new_image = Image(
            image_filename = filename,
            report_id = report_id
        )

        db.session.add(new_image)
        db.session.commit()

        print ("File uploaded!")

        return filename


@app.route('/')
def index():
    return render_template('what-happened.html')


@app.route('/someone-is-in-danger')
def someone_is_in_danger():
    return render_template('someone-is-in-danger.html')


@app.route('/someone-is-parked-in-a-bike-lane/step-2')
def someone_is_parked_in_a_bike_lane():
    return render_template('someone-is-parked-in-a-bike-lane/details.html')


@app.route('/geolocate')
def geolocate():
    return render_template('someone-is-parked-in-a-bike-lane/geolocate.html')

@app.route('/uploads/<filename>')
def view_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
