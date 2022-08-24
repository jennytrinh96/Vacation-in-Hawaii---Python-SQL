'''
Use Flask to create your routes, as follows:

* `/`

    * Homepage.

    * List all available routes.

* `/api/v1.0/precipitation`

    * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

    * Return the JSON representation of your dictionary.

* `/api/v1.0/stations`

    * Return a JSON list of stations from the dataset.

* `/api/v1.0/tobs`

    * Query the dates and temperature observations of the most active station for the previous year of data.

    * Return a JSON list of temperature observations (TOBS) for the previous year.

* `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

    * Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.

    * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.

    * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).

## Hints

* You will need to join the station and measurement tables for some of the queries.

* Use Flask `jsonify` to convert your API data into a valid JSON response object.

'''


# Import dependencies
from flask import Flask, jsonify
import numpy as np
import datetime as dt


import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

##############################################
# Database Setup
##############################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

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
def welcome():
    # List all available api routes
    return (
        f"<center>"
        f"Available Routes:<br/><br/>"
        f"Precipitation Data: <b><u>/api/v1.0/precipitation<br/></b></u>"
        f"List of Stations: <b><u>/api/v1.0/stations<br/></b></u>"
        f"Temperature Observations of 2016 - 2017: <b><u>/api/v1.0/tobs<br/></b></u>"
        f"Temperature Stat from Start Date (yyyy-mm-dd): <b><u>/api/v1.0/<start></b></u><br/>"
        f"Temperature Stat range Start - End Date (yyyy-mm-dd): <b><u>/api/v1.0/<start>/<end><b><u>"
        f"</center>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create session (link) from Python to the DB
    session = Session(engine)

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date > (dt.date(2017, 8, 23) - dt.timedelta(days=365))).all()

    session.close()

    # Create a dictionary from the query results
    rain_data = []
    for date, prcp in prcp_results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['prcp'] = prcp
        rain_data.append(prcp_dict)
    
    return jsonify(rain_data)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset
    results = session.query(Station.station, Station.name).all()
    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def observations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the previous year of data.

    stationCount = engine.execute('SELECT m.station, COUNT(m.station) FROM Measurement m GROUP BY m.station ORDER BY COUNT(m.station) DESC').fetchall()

    activeStation = stationCount[0].station

    results = session.query(Measurement.date, Measurement.tobs).\
                    filter((Measurement.station == activeStation) &
                           (Measurement.date > (dt.date(2017, 8, 18) - dt.timedelta(days= 365)))).all()

    session.close()


    # Return a JSON list of temperature observations (TOBS) for the previous year.
    temp_list = list(np.ravel(results))

    return jsonify(temp_list)



# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.

# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.

@app.route("/api/v1.0/<start>")
def start_date(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min, max, avg temps
    tobs_results = session.query(Measurement.date, func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs).filter(Measurement.date >= start)).all()

    # Close session
    session.close()

    # Create a dictionary from the query results
    temp_data = []
    for date, tMin, tMax, tAVG in tobs_results:
        tobs_dict = {}
        # tobs_dict['date'] = date
        tobs_dict['TMIN'] = tMin
        tobs_dict['TMAX'] = tMax
        tobs_dict['TAVG'] = tAVG
        temp_data.append(tobs_dict)
    
    # Jsonify
    return jsonify(temp_data)


# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min, max, avg temps
    tobs_results = session.query(Measurement.date, func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Close session
    session.close()

    # Create a dictionary from the query results
    temp_data = []
    for date, tMin, tMax, tAVG in tobs_results:
        tobs_dict = {}
        # tobs_dict['date'] = date
        tobs_dict['TMIN'] = tMin
        tobs_dict['TMAX'] = tMax
        tobs_dict['TAVG'] = tAVG
        temp_data.append(tobs_dict)
    
    # Jsonify
    return jsonify(temp_data)
    

# Launch app
if __name__ == '__main__':
    app.run(debug= True)
