#Dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///../Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station 

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<br/>"
    )

#Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    #Most Recent Date 1 Year Prior
    most_recent_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Query for the date and precipitation for the last year
    precipitation_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=most_recent_date).\
        order_by(Measurement.date).all()

    
    # Dict with date as the key and prcp as the value
    precipitation_data = []
    for date, prcp in precipitation_query:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation_data.append(precipitation_dict)

    return jsonify(precipitation_data)

#Stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.name).all()
    # Unravel results into a 1D array and convert to a list
    list_station = list(np.ravel(results))

    return jsonify(list_station)

#Tobs route 
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    session = Session(engine)  
    # Calculate the date 1 year ago from last date in database
    most_recent_date = dt.date(2017,8,23) - dt.timedelta(days=365)

    active_station_list= session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()

    primary_station = active_station_list[0][0]
    print(primary_station)

    # Query the primary station for all tobs from the last year
    primary = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == primary_station ).\
        filter(Measurement.date >=most_recent_date).\
        group_by(Measurement.date).all()

    # Unravel results into a 1D array and convert to a list
    yearly_temp = list(np.ravel(primary))

    # Return the results
    return jsonify(yearly_temp = yearly_temp)

#Temp Route
@app.route("/api/v1.0/temp")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    # calculate TMIN, TAVG, TMAX with start and stop
    # Unravel results into a 1D array and convert to a list
    stat_results = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        results = session.query(*stat_results).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    else:
        results = session.query(*stat_results).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)


if __name__ == '__main__':
    app.run()
