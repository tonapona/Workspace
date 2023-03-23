import requests
import pandas as pd
import urllib
import urllib3


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
    start = [49.9708458, 14.0564169]        # Televizni dokryvac Ded-Beroun
    stop = [50.0835581, 14.3951089]         # Petrinska rozhledna
    number_of_points = 20                   # Number of points to be examined for elevation

    # Calculation of latitudes and longitudes of examined points along the way of the relay link
    lat = []
    lon = []
    difference = [None]*2
    [difference[0], difference[1]] = [stop[0] - start[0], stop[1] - start[1]]
    for i in range(number_of_points):
        lat.append(start[0] + i*difference[0]/number_of_points)
        lon.append(start[1] + i*difference[1]/number_of_points)

    # Obtain the elevation of the calculated points
    data = pd.DataFrame({'lat': lat, 'lon': lon})
    data['elevation'] = data.apply(elevation_function, axis=1)
    data_csv = data.to_csv()

    # Process the data to find the point of maximum elevation
    data_rows = data_csv.split('\n')
    del data_rows[0]
    number_of_rows = len(data_rows)
    elevations = [None]*number_of_rows
    for i in range(number_of_rows):
        if i == 0 or i == number_of_rows - 1:
            elevations[i] = "0"
        else:
            elevations[i] = data_rows[i].split(',')[3]
    index_max = max(range(len(elevations)), key=elevations.__getitem__)

    # Output the results into the file ./results.txt
    with open(r"C:\\Workspace\\Uni\\grad\\SBS\\script\\results.txt", 'w') as file:
        file.write("Maximum elevation is at the point number " + str(index_max) + "!!\n----\n\n" + "num" + data_csv)
