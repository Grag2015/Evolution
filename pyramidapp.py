# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from pyramid.response import Response

from RoomsPack import calculation

def hello_world(request):
    print "request3333"
    # param = request.path.split('/')
    json_data = json.loads(request.environ['data'])
    print js['param']
    print "/request3333"

    return Response(
        calculation(json_data),
        content_type = 'application/json'
    )

config = Configurator()
# The router instance creates a request object by mapping the request URL to URL patterns provided by the route mapper
config.add_route('hello', '/') # maps a route to url и т.о. разные урлы могут обрабатываться разными функциями
config.add_view(hello_world, route_name='hello') #The add_view method of the Configurator object maps a request object to a callable response object, using the hello_world method
app = config.make_wsgi_app()