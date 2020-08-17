import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def homepage():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list.Return the JSON representation of your dictionary
    date_prcp = list(np.ravel(results))

    return jsonify(date_prcp)



@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Return a JSON list of stations from the dataset.
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    last_date = session.query(func.max(Measurement.date)).all()
    last_date = last_date[0][0]

    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    last_year = int(dt.datetime.strftime(last_date, '%Y'))
    last_month = int(dt.datetime.strftime(last_date, '%m'))
    last_day = int(dt.datetime.strftime(last_date, '%d'))

    first_date = dt.date(last_year, last_month, last_day) - dt.timedelta(days=365)
    first_date= dt.datetime.strftime(first_date, '%Y-%m-%d')
    
    station_count = session.query(Measurement.station,func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    station_id = station_count[0][0]
    
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= first_date).\
        filter(Measurement.station == station_id).all()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    temp = []
    for result in results:
        temp_dict = {}
        temp_dict["date"] = result[0]
        temp_dict["tobs"] = result[1]
        temp.append(temp_dict)

    return jsonify(temp)
    
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.   
@app.route("/api/v1.0/<start_date>")    
def start(start_date):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start_date).all()
    
    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    session = Session(engine)
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results = session.query(*sel).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    dates = []
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == '__main__':
    app.run(debug=True)
