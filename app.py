# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
database = automap_base()

# reflect the tables
database.prepare(autoload_with = engine)
database.classes.keys()

# Save references to each table
measurement = database.classes.measurement
station = database.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start_date<br/>"
            f"/api/v1.0/start_date/end_date<br/>"     
            f"**Start and end dates should be in YYYY-MM-DD format.**"       
            )

@app.route("/api/v1.0/precipitation")
def precip():
    print("Server received request for 'Precipitation' page...")

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    ending_date = dt.datetime.strptime(most_recent_date[0],"%Y-%m-%d")
    starting_date = ending_date - dt.timedelta(days=365)

    precip = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= starting_date).order_by(Measurement.date).all()
        
    data_dict=[]
    for element in precip:
        data_dict.append({element[0]:element[1]})

    return jsonify(data_dict)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")
    
    station_list = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()

    station_list_of_dicts = []
    for station in station_list:
        station_list_of_dicts.append({"Station":station[0], "Name":station[1], "Latitude":station[2], "Longitude":station[3], "Elevation":station[4]})

    return jsonify(station_list_of_dicts)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'Tobs' page...")

    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    ending_date = dt.datetime.strptime(most_recent_date[0],"%Y-%m-%d")
    starting_date = ending_date - dt.timedelta(days=365)

    temps_list = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date >= starting_date).all()

    temp_list_of_dicts = []
    for temp in temps_list:
        temp_list_of_dicts.append({"Date":temp[0], "Temperature":temp[1]})

    return jsonify(temp_list_of_dicts)

@app.route("/api/v1.0/<start>")
def start_only(start):
    print("Server received request for 'Start' page...")

    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()
    
    temp_stats_dict = {
        "TMIN":temp_stats[0][0],
        "TAVG":temp_stats[0][1],
        "TMAX":temp_stats[0][2]
    }

    return jsonify(temp_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def dates(start, end):
    print("Server received request for 'Start/End' page...")

    start_date = dt.datetime.strptime(start,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end,"%Y-%m-%d")

    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <=end_date).all()
    temp_stats_dict = {
        "TMIN":temp_stats[0][0],
        "TAVG":temp_stats[0][1],
        "TMAX":temp_stats[0][2]
    }

    return jsonify(temp_stats_dict)


session.close()


if __name__ == "__main__":
    app.run(debug=True)