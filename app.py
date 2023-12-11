# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base=automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
def one_year_ago():
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago_date = latest_date - dt.timedelta(days=365)
    return one_year_ago_date


@app.route("/")
def home():
    return (
        f"Welcome to the Climate API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        f"/api/v1.0/stations - List of stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the most active station in the last 12 months<br/>"
        f"/api/v1.0/<start> - Minimum, average, and maximum temperatures from the start date to the latest date<br/>"
        f"/api/v1.0/<start>/<end> - Minimum, average, and maximum temperatures for a specified date range<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session link to the database
    session = Session(engine)

    # Calculate the date one year ago
    one_year_ago_date = one_year_ago()

    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago_date).all()

    # Close the session
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create a session link to the database
    session = Session(engine)

    # Query for the list of stations
    results = session.query(Station.station).all()

    # Close the session
    session.close()

    # Convert the query results to a list
    station_list = [station for (station,) in results]

    # Return the JSON representation of the list
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create a session link to the database
    session = Session(engine)

    # Find the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year ago
    one_year_ago_date = one_year_ago()

    # Query for the temperature observations for the most active station in the last 12 months
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago_date).all()

    # Close the session
    session.close()

    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    # Return the JSON representation of the list
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    # Create a session link to the database
    session = Session(engine)

    # Convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d") if end else None

    # Query for temperature statistics based on start and end dates
    if end_date:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()

    # Close the session
    session.close()

    # Convert the query results to a list of dictionaries
    temperature_stats = [{"min": tmin, "avg": tavg, "max": tmax} for tmin, tavg, tmax in results]

    # Return the JSON representation of the list
    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug = True)
