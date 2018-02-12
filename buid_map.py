from geopy.geocoders import Nominatim
import folium


def read_file(path):
    '''(str) -> (list)
    This program reads data from file.
    Returns list of lists that consist of filminfo(name year etc) and location
    '''

    with open(path, encoding="utf-8", errors='ignore') as f:
        info = f.read()
        info = info.split("\n")
        res = []
        for line in info[14:-2]:
            first = line.split("\t")
            if "(" in first[-1]:
                location = first[-2]
            else:
                location = first[-1]

            res.append([first[0], location])
        return res


def loc_dict(data, year):
    '''(lst, int) -> (dict)
    This function returns dictionary with locations as keys and
    lists of movies as value
    '''

    res = dict()
    years = '(' + str(year)
    for line in data:
        if years in line[0]:
            film = line[0].split(years)
            location = line[-1]
            name_movie = film[0].replace("'", '"')
            if location in res:
                res[location] += [name_movie]
            else:
                res[location] = [name_movie]
    return res


def country_dict(data):
    '''(lst) -> (dict)
    This function returns dictionary with countries as keys and
    number of movies created for all time in the country as value
    '''

    res = dict()
    for line in data:
        loc = line[-1].replace(". ", ",")
        country = loc[loc.rfind(',')+1:].lstrip()
        if 'USA' in country:
            country = 'United States'
        elif 'UK' in country:
            country = 'United Kingdom'
        if country in res:
            res[country] += 1
        else:
            res[country] = 1
    return res


def check_num(country, data):
    '''(str, dict) -> (int)
    This function returns the number of movies created in the given country
    '''

    if country in data:
        return data[country]
    else:
        return 0


def get_coord(name):
    '''(str) -> (int, int)
    Returns a tuple of coordinates of given address.
    If the coordinates are not found it looks for approximate coordinate
    In case of error prints messege and returns None
    '''


    try:
        geolocator = Nominatim(timeout=20)
        location = geolocator.geocode(name)
        res = [location.latitude, location.longitude]
    except:
        new_name = name[name.find(",")+1:]
        if name != new_name:
            return get_coord(new_name)
        else:
            print("Location not found  ", new_name)
            return None
    return res


def build_map(locations, count):
    '''(dict, dict) -> None
    This function creates a map with two layears: first colors depending on
    overall number of movie created,
    second: markers of locations where movies where created in specific year
    '''

    my_map = folium.Map(location=[48.314775, 25.082925], zoom_start=2)
    layer1 = folium.FeatureGroup(name='Movies(red> 20000,\
                                        3000 <orange <20000, green < 3000)')
    layer1.add_child(folium.GeoJson(data=open('world.json', 'r',
                                    encoding='utf-8-sig').read(),
                                    style_function=lambda x: {'fillColor': 'green'
                                    if check_num(x['properties']["NAME"], count) < 3000
                                    else 'orange' if 3000 <= check_num(x['properties']["NAME"], count) <= 20000
                                    else 'red'}))
    my_map.add_child(layer1)
    my_map.save("Res_Map.html")
    layer2 = folium.FeatureGroup(name='Locations of movies in given year')
    for loc in locations:
        tag_film = ''
        for k in locations[loc]:
            tag_film += k + ", "
        locat = get_coord(loc)
        if locat is not None:
            layer2.add_child(folium.Marker(location=locat,
                             popup=tag_film, icon=folium.Icon()))
    my_map.add_child(layer2)
    my_map.add_child(folium.LayerControl())
    my_map.save("Res_Map.html")


def main():
    ''' None -> None
    This is the main function
    '''

    year = input("Enter a year: ")
    try:
        year = int(year)
    except:
        print("Year should be an integer!")
    all_data = read_file("locations.list")
    year_data = loc_dict(all_data, year)
    country = country_dict(all_data)
    build_map(year_data, country)


main()
