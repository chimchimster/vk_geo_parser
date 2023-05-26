
var photos = API.photos.search(
    {
    'q': '$20',
    'lat': '55.733647398995075',
    'long': '37.61603658440511',
    'count': 1000,
});
return photos;

var ph = API.wall.getById(
    {'posts': '-52456834_321045122',}
);
return ph;
