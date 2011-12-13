import httplib
import json

from ai import AI
from httplib import HTTPException
from time import sleep

url = 'localhost:80'


def sendCmd(conn, data):
	conn.request("POST", "/small_worlds", json.dumps(data))
	return json.loads(conn.getresponse().read()) 
	

def dispatch(conn, gameId):
	userInfo = sendCmd(conn, {'action' : 'aiJoin', 'gameId' : gameId})
	return AI(url, gameId, userInfo['sid'], userInfo['id'])
		
def main():	
	try:
		conn = httplib.HTTPConnection(url)
		while 1:
			gameList = sendCmd(conn, {'action' : 'getGameList'})['games']
			print gameList
			for game in gameList:
				aiNum = game['aiRequiredNum'] or 0
				for i in range(aiNum):
					print 'addiing up'
					dispatch(conn, game['gameId'])
			sleep(5)
	except HTTPException, e:
		print e
		conn.close()

if __name__ == "__main__":
	main()
			
					
			
			

