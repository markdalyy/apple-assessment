from flask import Flask, render_template
from database import get_db, close_db
from forms import LocationForm, WeatherForm
import os
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.teardown_appcontext(close_db)


@app.route("/")
@app.route("/all_locations")
def all_locations():
    db = get_db()
    locations = db.execute("""SELECT * FROM location;""").fetchall()
    return render_template("locations.html", caption="Locations", locations=locations)


@app.route("/all_weather")
def all_weather():
    db = get_db()
    weather = db.execute("""SELECT * FROM weather;""").fetchall()
    return render_template("weather.html", caption="All Weather", weather=weather)


@app.route("/weather_by_location", methods=["GET", "POST"])
def weather_by_location():
    form = LocationForm()
    weather = None
    location = None
    if form.validate_on_submit():
        location = form.location.data
        db = get_db()
        weather = db.execute("""SELECT * FROM weather
                                INNER JOIN location
                                ON weather.location_id=location.location_id
                                WHERE location_name = ?;""", (location,)).fetchall()
    return render_template("weather_by_location.html", form=form, caption=f"{location} Weather", weather=weather)


@app.route("/insert_weather", methods=["GET", "POST"])
def insert_weather():
    form = WeatherForm()
    message = ""
    if form.validate_on_submit():
        location = form.location.data
        time = form.time.data
        if time >= datetime.now():
            form.time.errors.append("Date must be in the past")  # records not predictions
        else:
            db = get_db()
            conflicting_weather = db.execute("""SELECT * FROM weather
                                                INNER JOIN location
                                                ON weather.location_id=location.location_id
                                                WHERE location_name = ? AND time_utc = ?;""",
                                             (location, time)).fetchone()
            if conflicting_weather is not None:
                form.time.errors.append("Record clashes with another!")
            else:
                pressure = form.pressure.data
                wind_direction = form.wind_direction.data
                wind_speed = form.wind_speed.data
                gust = form.gust.data
                db = get_db()
                db.execute("""INSERT INTO weather
                                        VALUES (?, ?, ?, ?, ?, ?);""",
                                     (location, time, pressure, wind_direction, wind_speed, gust))
                db.commit()
                message = "New record successfully inserted"
    return render_template("insert_weather.html", form=form, message=message)


@app.route("/count_records")
def count_records():
    db = get_db()
    weather = db.execute("""SELECT * FROM weather;""").fetchall()
    return str(len(weather))


@app.route("/data_table")
def data_table():
    db = get_db()
    weather = db.execute("""SELECT * FROM weather
                            LIMIT 100;""").fetchall()
    return render_template("data_table.html", weather=weather)
