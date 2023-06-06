import re
from adding_coordinates import CoordinatesCollector

with open('cities.txt', 'r') as cities:

    cities = [re.findall(r'(\d+[^,]*?|[а-яА-Я]\w+.\w+)', city) for city in cities.readlines()]

    list_of_coordinates = []
    for city in cities:
        c = CoordinatesCollector(city[3])
        coordinates = c.collect_coordinates()
        with open('test_city.txt', 'a') as file:
            file.write(','.join(city[:-1]) + ',' + coordinates[0] + '\n')