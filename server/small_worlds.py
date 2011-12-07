from path import join
from bottle import route, run, static_file, request, redirect
from sqlalchemy.exc import DatabaseError, DBAPIError, OperationalError
from misc import *

import bottle
import parseJson
import sys
import json
import traceback
import optparse
import actions
import misc_game
import misc

STATIC_FILES_ROOT = join("./client/")
PORT = 8080

app = bottle.app()
app.catchall = False

@route('/')
def serve_main():
    return static_file('main.html', STATIC_FILES_ROOT)

@route('/:root#css.*|images.*|js.*|maps.*#/:filename')
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
	misc.LOG_FILE = open(LOG_FILE_NAME, 'a')
	actions.doAction({'action': 'startAI'}, False)
	run(host='localhost', port=PORT)
	misc.LOG_FILE.close()
	return 0

if __name__ == '__main__':
	sys.exit(main())