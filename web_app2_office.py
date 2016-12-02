# -*- coding: utf-8 -*-
import socket
import StringIO
import sys
import json
import os
import re


class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # Create a listening socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        listen_socket.bind(server_address)
        # Activate
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

# The serve_forever() method will keep serving requests until Ctrl-C is used to stop the server.
    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # New client connection
            self.client_connection, client_address = listen_socket.accept()
            # Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            # пока объект класса WSGIServer существует, он обрабатывает запросы
            self.handle_one_request()

    def handle_one_request(self):
        #try:
        self.request_data = request_data = self.client_connection.recv(100000)#.decode('utf-8')
        print "type: ", self.client_connection
        # Print formatted request data a la 'curl -v'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))
        self.parse_request(request_data)
        print "выполніл parse_request(request_data)"
        # Construct environment dictionary using request data
        env = self.get_environ()
        print "выполніл self.get_environ()"

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.application(env, self.start_response)
        print "выполніл self.application(env, self.start_response)"
        # Construct a response and send it back to the client
        self.finish_response(result)
        print "выполніл self.finish_response(result)"
        # except AttributeError:
        #     self.client_connection.close()
        #     print "Error handle_one_request 1"
        # except:
        #     # Construct a response and send it back to the client
        #     self.client_connection.close()
        #     print "Unknown error handle_one_request"


    def parse_request(self, text):
        try:
            print "print text:" + text
            request_line = text.splitlines()[0]
            request_line2 = text.splitlines()[2]

            request_line = request_line.rstrip('\r\n')
            request_line2 = request_line2.rstrip('\r\n')
            # Break down the request line into components
            (self.request_method,  # GET
             self.path,            # /hello
             self.request_version  # HTTP/1.1
             ) = request_line.split()[0:3]
            #self.content_length = int(request_line2.replace("Content-Length: ", ""))
            self.data = (int(self.decode_geturl(re.search("width\=(\d+)", text).group(1))), int(self.decode_geturl(re.search("deep\=(\d+)", text).group(1))))
            print "self.data", self.data
            print "self.data type ", type(self.data)
        #print json.loads(self.data)
        except ValueError:
            # Construct a response and send it back to the client
            print "Error request1"
            self.client_connection.close()
        except IndexError:
            # Construct a response and send it back to the client
            self.client_connection.close()
            print "Error request1"
        except:
            # Construct a response and send it back to the client
            self.client_connection.close()
            print "Unknown error"



    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = StringIO.StringIO(self.request_data)
        print env['wsgi.input']
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        # env['CONTENT_LENGTH']    = self.content_length    # GET
        env['REQUEST_METHOD']    = self.request_method    # GET
        env['PATH_INFO']         = self.path              # /hello
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        env['data']       = self.data  # 8888
        return env

    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data
            # Print formatted response data a la 'curl -v'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            #print "connection keeps alive"
            self.client_connection.close()

    def decode_geturl(self, urlstr):
        urlstr = urlstr.replace("%7B", "{")
        urlstr = urlstr.replace("%7D", "}")
        urlstr = urlstr.replace("%5B", "[")
        urlstr = urlstr.replace("%5D", "]")
        urlstr = urlstr.replace("%22", '"')
        return urlstr

SERVER_ADDRESS = (HOST, PORT) = '', 1188


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()

# Для тестирования сервера
# import urllib2
# import json
#
# # send json request
# json_payload = json.dumps({'arrrrrrrrrr':1})
# headers = {'Content-Type':'application/json'}
# req = urllib2.Request('http://localhost:8888/', json_payload, headers)
# resp = urllib2.urlopen(req)
# response = resp.read()
# f.close()
# resp.getcode()
# resp.info()
# resp.geturl()

#     json_dict = [
#         {"BimType": "section", "Deep": 20.0, "Height": 3.0, "Id": 18, "Position": {"X": 0.0, "Y": 0.6, "Z": 0.0},
#          "Width": 30.0,
#          "ParentId": 4},
#         {"BimType": "section", "Deep": 15.0, "Height": 3.0, "Id": 19, "Position": {"X": 40.0, "Y": 0.6, "Z": 0.0},
#          "Width": 15.0, "ParentId": 4},
#         {"BimType": "section", "Deep": 20.0, "Height": 3.0, "Id": 20, "Position": {"X": 80.0, "Y": 0.6, "Z": 0.0},
#          "Width": 30.0, "ParentId": 4}]
# json_string = json.dumps(json_dict)
#
# # Для тестирования сервера
# import urllib2
# import json
#
# # send json request
# json_payload = json.dumps(json_dict)
# headers = {'Content-Type': 'application/json'}
# req = urllib2.Request('http://192.168.1.3:8888/section/', json_payload, headers)
# resp = urllib2.urlopen(req)
# response = resp.read()
#
# headers = {'Content-Type': 'text/plain'}
# req = urllib2.Request('http://192.168.1.3:8888/section?name=' + json_payload, headers=headers)
# resp = urllib2.urlopen(req)