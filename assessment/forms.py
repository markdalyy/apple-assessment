from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SubmitField
from wtforms.fields import DateTimeField
from wtforms.validators import InputRequired


class LocationForm(FlaskForm):
    location = StringField("Location:", validators=[InputRequired()])
    submit = SubmitField("Submit")


class WeatherForm(FlaskForm):
    location = StringField("Location:", validators=[InputRequired()])
    time = DateTimeField("Date and Time:", format='%Y-%m-%d %H:%M:%S', validators=[InputRequired()])
    pressure = FloatField("Atmospheric Pressure (mb):", validators=[InputRequired()])
    wind_direction = IntegerField("Wind Direction (degrees):", validators=[InputRequired()])
    wind_speed = FloatField("Wind Speed (kn):", validators=[InputRequired()])
    gust = FloatField("Gust (kn):", validators=[InputRequired()])
    submit = SubmitField("Submit")
