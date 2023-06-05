import webbrowser
from adding_coordinates import CoordinatesCollector

with open('cities.txt', 'r') as cities:

    cities = [city.split(' ')[1].strip() for city in cities.readlines()]

    lst = []
    for city in cities[1:]:
        x = CoordinatesCollector(city, webbrowser).collect_coordinates()[0]
        lst.append(x)
        print(x)
