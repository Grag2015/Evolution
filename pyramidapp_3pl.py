# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.response import Response

from mainSection2Rooms_3pl import calculation

def hello_world(request):
    print "request3333"
    # param = request.path.split('/')
    data_tuple = request.environ['data']
    file_obj = open('json_in_pl3.txt', "w")
    file_obj.write(str(data_tuple))
    file_obj.close()
    return Response(
       calculation(data_tuple),
        content_type = 'application/json'
    )

config = Configurator()
# The router instance creates a request object by mapping the request URL to URL patterns provided by the route mapper
config.add_route('hello', '{section}') # maps a route to url и т.о. разные урлы могут обрабатываться разными функциями
config.add_view(hello_world, route_name='hello') #The add_view method of the Configurator object maps a request object to a callable response object, using the hello_world method
app = config.make_wsgi_app()

