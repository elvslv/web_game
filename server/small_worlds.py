import sys
import os
import json

path = os.path.dirname(__file__)
sys.path.append(path)
os.chdir(path)

import parseJson
import misc

def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        try:
            request_body_size = int(environ['CONTENT_LENGTH'])
            request_body = environ['wsgi.input'].read(request_body_size)
        except BaseException, e:
            return 'Cannot read request body %s' % e
        try:
            misc.LAST_SID = 0
            response_body = parseJson.parseJsonObj(json.loads(request_body))
        except BaseException, e:
            response_body = 'An error %s occured while trying parse json: %s' % (e, request_body)
        status = '200 OK'
        headers = [('Content-type', 'text/plain'), ('Access-Control-Allow-Origin', '*')]
        start_response(status, headers)
        return json.dumps(response_body)
    else:
        response_body = ''
        status = '200 OK'
        headers = [('Content-type', 'text/html'),
                   ('Content-Length', str(len(response_body))),
                    ('Access-Control-Allow-Origin', '*')]
        start_response(status, headers)
        return [response_body]
