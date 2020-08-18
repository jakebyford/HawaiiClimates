import numpy as np
import os
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

os.chdir(os.path.dirname(os.path.abspath(__file__)))
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
session = Session(engine)
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    # Create our session (link) from Python to the DB
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all precipitation"""
    # Query all precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitation
    all_precipitation = []
    for date, prcp in results:
        precipitation_dict = {date : prcp}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a query of the most active station"""
    # Query most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.tobs)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.tobs).desc()).first()

    session.close()
    
    # Convert list of tuples into normal list
    # Query the last 12 months of temperature observation data for this station
    last_twelve_months_for_USC00519281 = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
    filter(Measurement.date >= '2016-08-23').\
    filter(Measurement.station == most_active_station[0]).\
    group_by(Measurement.date).\
    order_by(Measurement.date.desc()).all()

    return jsonify(last_twelve_months_for_USC00519281)

@app.route("/api/v1.0/start/end")
def start_end_range():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Create start date 
    start_date = '2017-07-04'
    #Create end date
    end_date = '2017-07-11'

    # Query the minimum temperature, the average 
    # temperature, and the max temperature 
    # for a given start or start-end range
    start_end_observations = session.query(Measurement.station, Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start_date).\
    filter(Measurement.date <= end_date).\
    group_by(Measurement.station).\
    order_by(Measurement.date.desc()).all()
    
    session.close()

    return jsonify(start_end_observations)

if __name__ == '__main__':
    app.run(debug=True)