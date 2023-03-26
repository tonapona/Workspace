import requests
import pandas as pd
import urllib
import urllib3
import geopy.distance
from numpy import sqrt
from time import sleep


# Performs a remote request and continues to make attempts until it succeeds
def make_remote_request(url: str, params: dict):
    count = 1
    while True:
        try:
            response = requests.get((url + urllib.parse.urlencode(params)))
        except (OSError, urllib3.exceptions.ProtocolError) as error:
            print('\n')
            print('*' * 20, 'Error Occured', '*' * 20)
            print(f'Number of tries: {count}')
            print(f'URL: {url}')
            print(error)
            print('\n')
            count += 1
            continue
        if not 'results' in response.json():
            sleep(0.5)
            continue
        break
    return response

def elevation_function(x):
    url = 'https://api.opentopodata.org/v1/eudem25m?'
    # Open-Elevation API might be used as an alternate source of elevation data but I haven't had any luck with it
    # url = 'https://api.open-elevation.com/api/v1/lookup?'
    params = {'locations': f"{x[0]},{x[1]}"}
    return make_remote_request(url, params).json()['results'][0]['elevation']


if __name__ == "__main__":
    # Input settings
    start = [50.0835, 14.395081]            # Petrinska rozhledna
    stop =  [49.9708, 14.056111]            # Televizni dokryvac Ded-Beroun
    number_of_points = 300                  # Number of points to be examined for elevation

    # Calculate of latitudes and longitudes of the specified number of examined points along the way of the raido relay link
    lat = []
    lon = []
    difference = [None]*2
    [difference[0], difference[1]] = [stop[0] - start[0], stop[1] - start[1]]
    for i in range(number_of_points + 1):
        lat.append(start[0] + i*difference[0]/number_of_points)
        lon.append(start[1] + i*difference[1]/number_of_points)

    # Obtain the elevation of the calculated points
    data = pd.DataFrame({'lat': lat, 'lon': lon})
    data['elevation'] = data.apply(elevation_function, axis=1)
    data_csv = data.to_csv()
    data_csv.replace("\r\n", "\n").replace("\r", "\n")  # CRLF -> LF

    # Process the data to find the point of maximum terrain elevation
    data_rows = data_csv.split('\n')
    del data_rows[0]
    number_of_rows = len(data_rows) - 1
    elevations = [None]*number_of_rows
    for i in range(number_of_rows):
        elevations[i] = data_rows[i].split(',')[3]
    index_max = max(range(len(elevations))[1:-1], key=elevations.__getitem__)
    point_max = data_rows[index_max].split(',')[1:3]

    # Calculate the radius of the first Fresnel zone F1
    f = 18                                              # frequency of the radio link in GHz
    d = geopy.distance.geodesic(start, stop)            # overall distance of the relay
    d1 = geopy.distance.geodesic(start, point_max)      # distance from start to the point of max elevation
    d2 = geopy.distance.geodesic(point_max, stop)       # distance from the point of max elevation to stop
    assert d - (d1 + d2) < 1e-04                        # adding the previous two should yield overall
    F1 = 17.3*sqrt((d1.km*d2.km)/(f*d.km))

    # Calculate the subrefraction height correction x
    R_Z = 6371000                                       # mean value of the Earth's radius in m
    k_e = 4/3                                           # value of the subrefractive factor k for normal atmosphere
    R_e = k_e*R_Z                                       # effective value of Earth's radius due to subrefraction
    x = (d1.m*d2.m)/(2*R_e)

    # Obtain antenna height at stop
    h1 = float(elevations[0]) + 60                      # fixed antenna height in start (Petrin - 60 m) including terrain elevation
    h0 = float(elevations[index_max])                   # maximum terrain elevation along the path

    # (h2 - h1)/d = ((h0 + x + F1) - h1)/d1, where h2 = elevation2 + Rxh
    Rxh = d.m*(h0 + x + F1 - h1)/d1.m + h1 - float(elevations[-1])

    # Output the results into the file ./results.txt
    with open(r"C:\\Workspace\\Uni\\grad\\SBS\\script\\results.txt", 'w') as file:
        file.write("The point of maximum elevation sits at [" + data_rows[index_max].split(',')[1] + "," + data_rows[index_max].split(',')[2] + "] with the rough elevation value of " + str(round(float(elevations[index_max]))) + " m.\n")
        file.write("Path-clearance calculation parameters: d = " + str(d) + ", d1 = " + str(d1) + ", d2 = " + str(d2) + ",\n")
        file.write("h0 = " + str(h0) + " m, F1 = " + str(F1) + " m, x = " + str(x) + " m.\n")
        file.write("Height of the antenna required for line-of-sight path clearance: Rxh = " + str(Rxh) + " m.\n")
        file.write("\n" + '*'*20 + "DATA" + '*'*20 + '\n' + "num" + data_csv)
