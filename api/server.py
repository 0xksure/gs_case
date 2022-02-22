from flask import request, Flask
from datetime import datetime
from flask_cors import CORS
from math import floor, ceil

import xarray
import datetime
import numpy as np
import h5json
import logging
app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "*"}})


def xarrayToGeoJson(xr, max_wave_height):

    hmax_array = xr.to_array()[0]
    longitudes = xr.longitude.values
    latitudes = xr.latitude.values
    lat_num_max = len(latitudes)-1
    lon_num_max = len(longitudes)-1
    geoJson = {"type": "Waves",
               "features": []}
    if(lat_num_max*lon_num_max >= 2000):
        return [geoJson,"too_many_points"]

    wave_sizes = ["small", "medium", "large"]

    for lat_index in range(0, lat_num_max):
        for lon_index in range(0, lon_num_max):
            wave_height = hmax_array[lat_index, lon_index].values.item(0)
            if not np.isnan(wave_height):

                wave_ratio = 2*wave_height/max_wave_height
                wave_size = wave_sizes[int(np.round(wave_ratio))]

                geoPoint = {
                    "type": "Feature",
                    "index": longitudes[lon_index].item(0)*latitudes[lat_index].item(0),
                    "properties": {
                        "name": "Max wave height",
                            "value": wave_height,
                            "size": wave_size,
                            "amenity": "wave",
                            "popupContent": "max wave height: " + str(wave_height)
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [longitudes[lon_index].item(0), latitudes[lat_index].item(0)]
                    },
                }
                geoJson["features"].append(geoPoint)

    return [geoJson,""]


def get_bounded_coordinates(lat_max, lat_min, lng_max, lng_min):
   
    data = xarray.open_dataset("~/Documents/datasets/waves.nc")
    some_date = datetime.date.fromisoformat("2019-01-01")
    selected_time_data = data.sel(time="2019-01-01T00:00:00")
    max_wave_height = np.max(
        np.nan_to_num(selected_time_data["hmax"].values))
    selected_coord = selected_time_data.sel(latitude=range(
        lat_min, lat_max+1), longitude=range(lng_min, lng_max+1))

    return xarrayToGeoJson(selected_coord, max_wave_height)


# Get bounds
#
@app.route("/bounds", methods=["POST"])
def bounds():
    print("json: ", request.json)
    body = request.json["body"]
    lat_max = body["latMax"]
    lat_min = body["latMin"]
    lng_max = body["lngMax"]
    lng_min = body["lngMin"]
    if (lat_max is None) | (lat_min is None) | (lng_max is None) | (lng_min is None):
        logging.error("Error! With data ({lat_max},{lat_min},{lng_max},{lng_min})".format(
            lat_max=int(lat_max), lat_min=int(lat_min), lng_max=int(lng_max), lng_min=int(lng_min)))
        return ("error", 500)

    lat_max = int(ceil(lat_max))
    lat_min = int(floor(lat_min))
    lng_max = int(ceil(lng_max))
    lng_min = int(floor(lng_min))
    bounded_res = get_bounded_coordinates(
        lat_max, lat_min, lng_max, lng_min)
    if bounded_res[1] != "":
        return (bounded_res[0],204)
    return bounded_res[0]


if __name__ == '__main__':
    app.run()
