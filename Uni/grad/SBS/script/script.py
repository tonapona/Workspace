import requests
import pandas as pd
import urllib
import urllib3
import geopy.distance
from numpy import sqrt
from math import ceil
from time import sleep

TRANSMITTERS = {
    "Praha Slivenec": [50.02011399999999, 14.34015700000002, 10],
    "Bubovice": [49.9724979999999, 14.17755099999998, 10],
    "Zlicin": [50.05122599999999, 14.28301700000001, 10],
    "Rudna": [50.018478, 14.19571300000003, 10],
    "Chyne": [50.018478, 14.19571300000003, 10],
    "Strahov": [50.07985277777778, 14.37583333333333, 60],
    "Beroun-Zavodi": [49.97116999999999, 14.111799, 10],
}

def get_elevation(point):
    url = 'https://api.opentopodata.org/v1/eudem25m?'
    query = {'locations': f"{point[0]},{point[1]}"}
    while True:
        try:
            response = requests.get((url + urllib.parse.urlencode(query)))
        except (OSError, urllib3.exceptions.ProtocolError) as ex:
            print('*' * 20, 'Error Occured', '*' * 20)
            print(ex)
            continue
        if not 'results' in response.json():
            sleep(0.5)
            continue
        break
    return response.json()['results'][0]['elevation']

def path_clearance(transmitter1, transmitter2):
    ## Initialization
    start = TRANSMITTERS[transmitter1]
    stop =  TRANSMITTERS[transmitter2]
    Rx = transmitter2
    if get_elevation(start[0:2]) > get_elevation(stop[0:2]): start, stop = stop, start, Rx = transmitter1

    ## Inspect the path of the radio link for elevation every 100 meters
    d = geopy.distance.geodesic(start[0:2], stop[0:2])
    number_of_points = ceil(d.m/100)
    # number_of_points = 10     # small number of points for debugging

    lat = []
    lon = []
    difference = [stop[0] - start[0], stop[1] - start[1]]
    for i in range(number_of_points + 1):
        lat.append(start[0] + i*difference[0]/number_of_points)
        lon.append(start[1] + i*difference[1]/number_of_points)

    data = pd.DataFrame({'lat': lat, 'lon': lon})
    data['elevation'] = data.apply(get_elevation, axis=1)
    data_csv = data.to_csv(header=None, lineterminator='\n')

    ## Process the data to find the point of maximum terrain elevation
    data_rows = data_csv.split('\n')
    number_of_rows = len(data_rows) - 1
    elevations = [None]*number_of_rows
    for i in range(number_of_rows):
        elevations[i] = data_rows[i].split(',')[3]
    index_max = max(range(len(elevations))[1:-1], key=elevations.__getitem__)
    point_max = data_rows[index_max].split(',')[1:3]

    ## Calculate the radius of the first Fresnel zone F1
    f = 18                                                  # frequency of the radio link in GHz
    d1 = geopy.distance.geodesic(start[0:2], point_max)     # distance from start to the point of max elevation
    d2 = geopy.distance.geodesic(point_max, stop[0:2])      # distance from the point of max elevation to stop
    assert d - (d1 + d2) < 1e-04                            # adding the previous two should yield overall
    F1 = 17.3*sqrt((d1.km*d2.km)/(f*d.km))

    ## Calculate the subrefraction height correction x
    R_Z = 6371000                                           # mean value of the Earth's radius in m
    k_e = 4/3                                               # value of the subrefractive factor k for normal atmosphere
    R_e = k_e*R_Z                                           # effective value of Earth's radius due to subrefraction
    x = (d1.m*d2.m)/(2*R_e)

    ## Obtain antenna height at stop
    h1 = float(elevations[0]) + start[2]                    # fixed antenna height in start including terrain elevation
    h0 = float(elevations[index_max])                       # maximum terrain elevation along the path
    Rxh = d.m*(h0 + x + F1 - h1)/d1.m + h1 - float(elevations[-1])

    ## Output the results into a file
    with open(fr"C:\\Workspace\\Uni\\grad\\SBS\\script\\{transmitter1}_{transmitter2}_{number_of_points}points.txt", 'w') as file:
        file.write('*'*20 + "PATH-CLEARANCE" + '*'*20 + "\n")
        file.write("Point of maximum elevation h0: [" + point_max[0] + "," + point_max[1] + "]\n")
        file.write("Parameters: d = " + str(round(d.km,2)) +" km, d1 = " + str(round(d1.km,2)) + " km, d2 = " + str(round(d2.km,2)) + " km, h1 = (" + str(round(float(elevations[0]))) + " + " + str(round(start[2])) + ") m, h0 = " + str(round(h0,2)) + " m, F1 = " + str(round(F1,2)) + " m, x = " + str(round(x,2)) + " m\n")
        file.write("Height of the " + Rx + " antenna required for line-of-sight path clearance: Rxh = " + str(round(Rxh,2)) + " m\n")
        file.write("\n" + '*'*20 + "DATA" + '*'*20 + '\n' + data_csv)


if __name__ == "__main__":
    ## Path clearance function with user input
    path_clearance("Strahov", "Beroun-Zavodi")
