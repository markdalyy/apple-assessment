from flask import Flask, render_template, url_for
from MySQL.db import db
from forms import LocationForm, WeatherForm
import os
from datetime import datetime
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
#app.teardown_appcontext(db.close_connection())


@app.route("/")
@app.route("/all_locations")
def all_locations():
    locations = db.execute_stmt("""SELECT * FROM location;""")
    return render_template("locations.html", caption="Locations", locations=locations)


@app.route("/all_weather")
def all_weather():
    weather = db.execute_stmt("""SELECT * FROM weather;""")
    return render_template("weather.html", caption="All Weather", weather=weather)


@app.route("/weather_by_location", methods=["GET", "POST"])
def weather_by_location():
    form = LocationForm()
    weather = None
    location = None
    if form.validate_on_submit():
        location = form.location.data
        cursor = db.connection.cursor()
        cursor.execute("""SELECT location_name, weather.location_id, time_utc, atmospheric_pressure_mb,
                                wind_direction_degree, wind_speed_kn, gust_kn FROM weather
                            INNER JOIN location
                            ON weather.location_id=location.location_id
                            WHERE location_name = %s;""", (location,))
        weather = cursor.fetchall()
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
            cursor = db.connection.cursor()
            cursor.execute("""SELECT * FROM weather
                            INNER JOIN location
                            ON weather.location_id=location.location_id
                            WHERE location_name = %s AND time_utc = %s;""",
                            (location, time))
            conflicting_weather = cursor.fetchone()
            if conflicting_weather is not None:
                form.time.errors.append("Record clashes with another!")
            else:
                pressure = form.pressure.data
                wind_direction = form.wind_direction.data
                wind_speed = form.wind_speed.data
                gust = form.gust.data
                cursor = db.connection.cursor()
                cursor.execute("""INSERT INTO weather
                                        VALUES (%s, %s, %s, %s, %s, %s);""",
                                     (location, time, pressure, wind_direction, wind_speed, gust))
                db.connection.commit()
                message = "New record successfully inserted"
    return render_template("insert_weather.html", form=form, message=message)


@app.route("/bar_chart")
def bar_chart():
    location_names = db.execute_stmt("""SELECT location_name FROM location;""")
    plot_locations = []
    for name in location_names:
        plot_locations.append(name[0])
    y_pos = np.arange(len(plot_locations))
    avg_wind_speeds = db.execute_stmt("""SELECT AVG(wind_speed_kn) FROM weather
                        GROUP BY location_id;""")
    plot_wind_speeds = []
    for speed in avg_wind_speeds:
        plot_wind_speeds.append(speed[0])
    plt.figure(figsize=(10, 5))  # adjust the size of plot
    plt.bar(y_pos, plot_wind_speeds, align='center', alpha=0.5)
    plt.xticks(y_pos, plot_locations)
    plt.ylabel('Wind Speed')
    plt.title('Average Wind Speed by Location')

    # plt.show()
    plt.tight_layout()
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/images/chart.png")
    plt.savefig(path)

    return render_template("bar_chart.html")
