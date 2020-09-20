import os
from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template
import secrets
from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import secretstuff

import jsonhandler

from datetime import datetime


# Define flask variables
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secretstuff.secret_key
website_url = "http://localhost:5000/"

# DB initialisation
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)


# Define DB models
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String)
    report_unique_id = db.Column(db.Integer)

    def image_url(self):
        return website_url + "/static/uploads/" + self.image_filename


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reason_for_report = db.Column(db.String)
    company_name = db.Column(db.String)
    registration_number = db.Column(db.String)
    vehicle_colour = db.Column(db.String)
    vehicle_brand = db.Column(db.String)
    details_body = db.Column(db.String)
    location_road_name = db.Column(db.String)
    location_postcode = db.Column(db.String)
    location_city_name = db.Column(db.String)
    location_latitude = db.Column(db.Integer)
    location_longitude = db.Column(db.Integer)
    when_did_this_happen = db.Column(db.String)
    council_name = db.Column(db.String)
    report_unique_id = db.Column(db.String)
    timestamp = db.Column(db.DateTime)

    def report_unique_url(self):
        return website_url + "report/" + self.report_unique_id


# START: UPLOAD AND SERVE IMAGES

@app.route('/upload_file/to/<report_unique_id>', methods=['POST'])
def upload_file(report_unique_id = None):

    # check if report ID provided
    if report_unique_id is None:
        print ("No associated report ID")
        flash ("No associated report ID")
        return "No associated report ID"

    # check if the post request has a file
    if 'file' not in request.files:
        flash('No file part')
        return "No file part"

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
            report_unique_id = report_unique_id
        )

        db.session.add(new_image)
        db.session.commit()

        print ("File uploaded!")

        return filename


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/view_image/<filename>')
def view_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# END: UPLOAD AND SERVE IMAGES


# Above my pay grade...
@app.route('/someone-is-in-danger')
def someone_is_in_danger():
    return render_template('someone-is-in-danger.html')


# Helper functions (DRY, amirite?)

def report_unique_id_status(report_unique_id):

    # Check it is not None
    if report_unique_id is None:
        return ("No unique report ID provided")

    # ... and check that it exists
    report_count = Report.query.filter_by(report_unique_id=report_unique_id).count()
    if report_count == 0:
        return ("No record found with unique_id = " + report_unique_id)

    return "valid"


# START: BIKE LANE ENDPOINTS
@app.route('/someone-is-parked-in-a-bike-lane/details', methods=['GET', 'POST'])
def bike_lane_details():

    if request.method == 'GET':
        return render_template('someone-is-parked-in-a-bike-lane/details.html',
                               report_unique_id = report_unique_id,
                               company_list = jsonhandler.company_list())

    if request.method == 'POST':
        # Get input from forms and put into vars
        company_name = request.form.get('company-name')
        registration_number = request.form.get('registration-number')
        vehicle_colour = request.form.get('vehicle-colour')
        vehicle_brand = request.form.get('vehicle-brand')
        details_body = request.form.get('details-body')
        when_did_this_happen = request.form.get('when-did-this-happen')

        # Do some basic error checking, proceed if all ok
        if company_name is None or registration_number is None:
            flash ("You need to provide basic details")
            return redirect(request.url)

        # Create new record
        report_unique_id = secrets.token_hex(5)
        new_report = Report(
            # id is set automatically
            report_unique_id = report_unique_id,
            reason_for_report = "Parking in a bike lane",
            company_name = company_name,
            registration_number = registration_number,
            vehicle_colour = vehicle_colour,
            vehicle_brand = vehicle_brand,
            details_body = details_body,
            timestamp = datetime.utcnow(),
            when_did_this_happen = when_did_this_happen
        )

        db.session.add(new_report)
        db.session.commit()

        return redirect(url_for('bike_lane_where', report_unique_id=report_unique_id))


@app.route('/someone-is-parked-in-a-bike-lane/where/<report_unique_id>', methods=['GET', 'POST'])
def bike_lane_where(report_unique_id):

    # Check the unique_id provided is valid, return error if not
    report_status = report_unique_id_status(report_unique_id)
    if report_status != "valid":
        flash (report_status)
        return report_status

    if request.method == 'GET':
        return render_template('someone-is-parked-in-a-bike-lane/where.html',
                               report_unique_id=report_unique_id)

    if request.method == 'POST':
        # Get the data from the form
        road_name = request.form.get('road-name')
        city_name = request.form.get('city-name')
        postcode = request.form.get('postcode')
        council_name = request.form.get('council-name')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')


        # Check basic details provided
        if road_name is None or city_name is None:
            flash("You need to provide basic details")
            return redirect(request.url)

        # Load the report from the DB
        report = Report.query.filter_by(report_unique_id=report_unique_id).first()

        # Add the new fields
        report.location_road_name = road_name
        report.location_city_name = city_name
        if postcode is not None: report.location_postcode = postcode
        if council_name is not None: report.council_name = council_name
        if latitude is not None and longitude is not None:
            report.location_latitude = latitude
            report.location_longitude = longitude

        db.session.commit()

        return redirect(url_for('bike_lane_photos', report_unique_id=report_unique_id))


@app.route('/someone-is-parked-in-a-bike-lane/photos/<report_unique_id>', methods=['GET', 'POST'])
def bike_lane_photos(report_unique_id):

    # Check the unique_id provided is valid, return error if not
    report_status = report_unique_id_status(report_unique_id)
    if report_status != "valid":
        flash (report_status)
        return report_status

    if request.method == 'GET':
        return render_template('generic/upload-photos.html', report_unique_id = report_unique_id)

    if request.method == 'POST':
        # This will only be allowed if photos have been uploaded - checked clinet side
        return redirect(url_for('submit_report', report_unique_id))


# END: BIKE LANE ENDPOINTS


# START: VIEW REPORTS

@app.route('/view/<report_unique_id>')
def view_report(report_unique_id):

    # Check the unique_id provided is valid, return error if not
    report_status = report_unique_id_status(report_unique_id)
    if report_status != "valid":
        flash(report_status)
        return report_status

    # Load the report and the photos from the DB
    report = Report.query.filter_by(report_unique_id=report_unique_id).first()
    images = Image.query.filter_by(report_unique_id=report_unique_id).all()

    # Show the report
    return render_template('view-report.html', report=report, images=images)


# END: VIEW REPORTS

# The main event...

@app.route('/')
def index():
    return render_template('what-happened.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008, debug=True)
