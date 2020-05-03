import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify, request, render_template
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect the db into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# set references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# create a session link from python to DB
session = Session(engine)

# design a Flask API based on the queries from Climate Analysis 
# create an app instance for Hawaii climate data API 
app = Flask(__name__)

# define the routes
@app.route("/")
def homepage():
    return render_template("index.html")
 
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return total preciptation data"""
    # Query all measurments
    results = session.query(Measurement).all()

    # Create a dictionary from the row data and append to a list
    prcp_data = []
    for result in results:
        result_dict = {}
        result_dict["date"] = result.date
        result_dict["prcp"] = result.prcp
        prcp_data.append(result_dict)

    return jsonify(prcp_data)   

@app.route("/api/v1.0/stations")
def stations():
    """Return station data"""
    Station = Base.classes.station
    # Query stations and return a JSON list of stations from the datase
    station_results = session.query(Station).all()

    # Create a dictionary from the row data and append to a list
    station_list = []
    for result in station_results:
        station_dict = {}
        station_dict["station"] = result.station
        station_dict["name"] = result.name
        station_list.append(station_dict)
    return jsonify(station_list)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def temperatures():
    Measurement = Base.classes.measurement
    """Return temperature data"""
    # get the last date
    get_last_date = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).limit(1)
    last_date = get_last_date[0][0]

    # calculate the date one year before last measurement
    start_date = dt.datetime.strftime((dt.datetime.strptime\
        (last_date,'%Y-%m-%d') - dt.timedelta(days=365))\
            .date(),'%Y-%m-%d')

# Query the Measurements for days after and including start date
    results = session.query(Measurement).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date)\
    .order_by(Measurement.date).all()

    # # Create a dictionary from the row data and append to a list
    tobs_temps = []
    for result in results:
        temp_dict = {}
        temp_dict["date"] = result.date
        temp_dict["tobs"] = result.tobs
        tobs_temps.append(temp_dict)

    return jsonify(tobs_temps)

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range

@app.route("/api/v1.0/onetemp/<string:date1>")
def onedate(date1):
    Measurement = Base.classes.measurement
    """Return temperature data"""
    try:
        (date1)
    except ValueError:
        return f"The date {date1} is not in the correct format or is invalid"

    results = session.query(func.min(Measurement.tobs).label('min'), \
    func.avg(Measurement.tobs).label('avg')\
    , func.max(Measurement.tobs).label('max')).\
    filter(Measurement.date >= date1).all()
    
    # Unravel the results
    stats = list(np.ravel(results))
    tmp_stats = []
    for result in results:
        result_dict = {}
        result_dict["min"] = result.min
        result_dict["avg"] = result.avg
        result_dict["max"] = result.max
        tmp_stats.append(result_dict)

    return jsonify(tmp_stats)

# When given the start and the end date, calculate the TMIN, TAVG, 
# and TMAX for dates between the start and end date inclusive

@app.route("/api/v1.0/twotemp/<string:date1>/<string:date2>")
def twodates(date1, date2):

    try:
        (date1)
        (date2)
    except ValueError:
        return f"The date {date1} or {date2} is not in the correct format or is invalid"

    Measurement = Base.classes.measurement

    results = session.query(func.min(Measurement.tobs).label('min'),\
     func.avg(Measurement.tobs).label('avg')\
    , func.max(Measurement.tobs).label('max')).\
    filter(Measurement.date >= date1).filter(Measurement.date <= date2).all()
    
    #Unravel the results
    tmp_stats = []
    for result in results:
        result_dict = {}
        result_dict["min"] = result.min
        result_dict["avg"] = result.avg
        result_dict["max"] = result.max
        tmp_stats.append(result_dict)

    return jsonify(tmp_stats)

if __name__ == '__main__':
    app.run(debug=True)
