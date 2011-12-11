import sys
import os
import json

#from twisted.web.wsgi import WSGIResource
#from twisted.internet import reactor

path = os.path.dirname(__file__)
sys.path.append(path)
os.chdir(path)

import parseJson
import misc

def application(environ, start_response):
    print 'fhsjghjs'
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            print 1
            request_body_size = int(environ['CONTENT_LENGTH'])
            print 2
            request_body = environ['wsgi.input'].read(request_body_size)
        except BaseException, e:
            return 'Cannot read request body %s' % e
        try:
            print 3
            misc.LAST_SID = 0
            print 4
            print request_body
            response_body = parseJson.parseJsonObj(json.loads(request_body))
            print 5
        except BaseException, e:
            response_body = 'An error %s occured while trying parse json: %s' % (e, request_body)
        status = '200 OK'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        print response_body
        return json.dumps(response_body)
    else:
        response_body = ''
        status = '200 OK'
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response_body)))]
        start_response(status, headers)
        return [response_body]

#resource = WSGIResource(reactor, reactor.getThreadPool(), application)