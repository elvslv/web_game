import httplib
import json

from ai import AI
from advanced_ai import AdvancedAI
from httplib import HTTPException
from time import sleep

url = 'localhost:80'
AI_INST = AdvancedAI

def sendCmd(conn, data):
	conn.request("POST", "/small_worlds", json.dumps(data))
	return json.loads(conn.getresponse().read()) 
	

def dispatch(conn, gameId, logFile):
	userInfo = sendCmd(conn, {'action' : 'aiJoin', 'gameId' : gameId})
	return AI_INST(url, gameId, userInfo['sid'], userInfo['id'], logFile)
		
def main():	
	logFilesCnt = 0
	try:
		conn = httplib.HTTPConnection(url)
		while 1:
			gameList = sendCmd(conn, {'action' : 'getGameList'})['games']
			for game in gameList:
				aiNum = game['aiRequiredNum'] or 0
				if aiNum:
					logFile = open('logs\\ai_results%d.log' % logFilesCnt, 'w')
					logFilesCnt += 1
					for i in range(aiNum):	dispatch(conn, game['gameId'], logFile)
			sleep(5)
	except HTTPException, e:
		print e
		conn.close()

if __name__ == "__main__":
	main()
			
					
			
			

