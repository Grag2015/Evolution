# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.response import Response

from mainSection2Rooms import calculation

def hello_world(request):
    print "request3333"
    # param = request.path.split('/')
    json_string = request.environ['data']
    print "/request3333"
    file_obj = open('json_in.txt', "w")
    file_obj.write(json_string)
    file_obj.close()
    json_resp = calculation(json_string)
    if json_resp != 0:
        return Response(
            json_resp,
            content_type = 'application/json'
        )
    else:
        return 0

config = Configurator()
# The router instance creates a request object by mapping the request URL to URL patterns provided by the route mapper
config.add_route('hello', '{section}') # maps a route to url и т.о. разные урлы могут обрабатываться разными функциями
config.add_view(hello_world, route_name='hello') #The add_view method of the Configurator object maps a request object to a callable response object, using the hello_world method
app = config.make_wsgi_app()
