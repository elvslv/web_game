from utils.path import join
from bottle import route, run, static_file, request, app
import bottle
import parseJson
import misc
import sys
import json
import traceback
import optparse

STATIC_FILES_ROOT = join("./client/")
PORT = 3030

@route('/')
def serve_main():
    return static_file('main.html', STATIC_FILES_ROOT)

@route('/:root#css.*|images.*|js.*#/:filename')
def serve_dirs(root,filename):
    return static_file(filename, join(STATIC_FILES_ROOT, root))

@route('/ajax', method='POST')
def serve_ajax():
    try:
        return parseJson.parseJsonObj(json.load(request.body))
    except Exception, e:
        traceback.print_exc()
        return e

def main():
	run(reloader=True, host='localhost', port=PORT)
	return 0

if __name__ == '__main__':
    sys.exit(main())
