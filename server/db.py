from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_MAPNAME_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN
from gameExceptions import BadFieldException
from sqlalchemy import create_engine, Table, Boolean, Column, Integer, String, MetaData, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import sessionmaker, relationship, backref, join
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

import misc
import checkFields
import sys

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

DB_STRING =  """mysql+mysqldb://%s:%s@%s:%d/%s""" % \
	(DATABASE_USER, DATABASE_PASSWD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME)


Base = declarative_base()

string = lambda len: Column(String(len))
uniqString = lambda len: Column(String(len), unique=True, nullable=False)
pkey = lambda: Column(Integer, primary_key=True)
fkey = lambda name: Column(Integer, ForeignKey(name, onupdate='CASCADE', ondelete='CASCADE'))
requiredInteger = lambda: Column(Integer, nullable=False)


class Map(Base):
	__tablename__ = 'maps'

	id = pkey()
    	name = uniqString(MAX_MAPNAME_LEN)
   	playersNum = Column(Integer)
    	turnsNum = Column(Integer)
    
    	def __init__(self, name, playersNum, turnsNum): 
    		self.name = name
    		self.playersNum = playersNum
    		self.turnsNum = turnsNum

	def getRegion(self, regionId):
		region = filter(lambda x: x.id == regionId, self.regions)
		if not region: raise BadFieldException('badRegionId')
		return region[0]

class Game(Base):
	__tablename__ = 'games'

    	id = pkey()
    	name = uniqString(MAX_GAMENAME_LEN)
    	descr = string(MAX_GAMEDESCR_LEN)
    	state = Column(Integer)
    	turn = Column(Integer)
    	activePlayerId = Column(Integer)
    	mapId = fkey('maps.id')
  
    	map = relationship(Map)
    	
    	
    	def __init__(self, name, descr, map): 
    		self.name = name
        	self.descr = descr
        	self.turn = 0
        	self.state = misc.GAME_WAITING
        	self.map = map

        def getTokenBadge(self, position):
        	tokenBadge = filter(lambda x: x.pos == position, self.tokenBadges)
        	if not tokenBadge: raise BadFieldException('badPosition')
        	return tokenBadge[0]

        def checkStage(self, state, user):
        	lastEvent = self.history[-1]
		badStage = lastEvent.state not in misc.possiblePrevCmd[state] 
		if lastEvent.state == misc.GAME_CONQUER:
				battle = lastEvent.warHistory
				agressor = battle.agressorBadge
        			war = agressor and not agressor.currentTokenBadge.inDecline
        			if state == misc.GAME_DEFEND:
					if  battle.attackType == misc.ATTACK_ENCHANT or user.currentTokenBadge.inDecline:
						badStage = True
#				elif attackedTokensNum > 1: badStage = True  			What's going on here?
		if badStage or user.id != self.activePlayerId:
			raise BadFieldException('BadStage')
			



        def getDefendingRegionInfo(self, player):
        	lastWarHistoryEntry = self.warHistory[-1]
        	if lastWarHistoryEntry.victimBadge.id != player.currentTokenBadge.id:
			raise BadFieldException('badStage')
		return lastWarHistoryEntry.conqRegion

	def getNextPlayer(self):
        	try:
        		return dbi.query(User).filter(User.priority > activePlayer.priority).one()
        	except NoResultFound:
        		return None

        def getLastState(self):
        	return self.history[-1].state

	def prepareForNextTurn(self, newActPlayer):
		self.activePlayer = newActPlayer
		clearGameStateAtTheEndOfTurn(gameId)
		if newActPlayer.currentTokenBadge.id:
			addUnits =  callRaceMethod(newActPlayer.currentTokenBadge.raceId,
				'countAdditionalConquerUnits', newActPlayer, gameId)
			newActPlayer.tokensInHand += addUnits -len(newActPlayer.regions) + newActPlayer.currentTokenBadge.totalTokensNum
			for region in newActPlayer.regions:
				region.tokensNum = 1

	def getNonEmptyConqueredRegions(self, tokenBadge):
		return len(filter(lambda x: x.agressorBadge == tokenBadge and agressorTokensNum > 0, warHistory))

class TokenBadge(Base):
	__tablename__ = 'tokenBadges'

    	id = pkey()
    	gameId = fkey('games.id')
    	raceId = Column(Integer)
    	specPowId = Column(Integer)
    	pos = Column(Integer, default=0)
    	bonusMoney = Column(Integer, default = 0)
    	inDecline = Column(Boolean, default=False)
    	totalTokensNum = Column(Integer, default = 0)

    	game = relationship(Game, backref=backref('tokenBadges'))

 	def __init__(self, raceId, specPowId, gameId): 
 		self.raceId = raceId
        	self.specPowId = specPowId
        	self.gameId = gameId

        def isNeighbor(self, region):
        	for reg in self.regions:
        		if region.adjacent(reg):
        			return True
        	return False
        
class User(Base):
	__tablename__ = 'users'

    	id = pkey()
    	name = uniqString(MAX_USERNAME_LEN)
    	password = string (MAX_PASSWORD_LEN)
    	sid = Column(Integer, unique=True)
    	gameId = fkey('games.id')
    	isReady = Column(Boolean, default=False)
    	currentTokenBadgeId = fkey('tokenBadges.id')
    	declinedTokenBadgeId = fkey('tokenBadges.id')
    	coins = Column(Integer, default=misc.INIT_COINS_NUM)
    	tokensInHand = Column(Integer, default = 0)
	priority = Column(Integer)

	
    	game = relationship(Game, backref=backref('players', order_by=priority))
    	currentTokenBadge = relationship(TokenBadge, backref=backref('owner'), primaryjoin=currentTokenBadgeId==TokenBadge.id)
    	declinedTokenBadge = relationship(TokenBadge, primaryjoin=declinedTokenBadgeId==TokenBadge.id)

    	def __init__(self, username, password):
    		self.name = username
        	self.password = password

        def checkForFriends(self, attackedUser):			
        	if not attackedUser: return
		turn = self.game.turn -  int(self.priority < attackedUser.priority) ## Cryptic code mercilessly plagiarized without analysis 
		histEntry = dbi.query(HistoryEntry).filter(HistoryEntry.id==self.game.id).\
									filter(HistoryEntry.turn==turn)
		if histEntry.state == misc.GAME_CHOOSE_FRIEND and histEntry.user == self 	and histEntry.friend == attackedUser:

			raise BadFieldException('UsersAreFriends')

	def decline(self):
		for declinedRegion in self.declinedTokenBadge.regions:
			declinedRegion.owner = None
			declinedRegion.inDecline = False
		self.declinedTokenBadge = self.currentTokenBadge
		for region in self.regions:
			region.tokensNum = 1
			region.inDecline = True
		self.currentTokenBadge.inDecline = True
		self.currentTokenBadge.totalTokensNum = len(self.regions)
			
class Region(Base):
    __tablename__ = 'regions'

    id = pkey()
    mapId = fkey('maps.id')
    defTokensNum = Column(Integer, default = 0)

    border = Column(Boolean, default=False)
    coast = Column(Boolean, default=False)
    mountain = Column(Boolean, default=False)
    sea = Column(Boolean, default=False) 
    mine = Column(Boolean, default=False) 
    farmland = Column(Boolean, default=False) 
    magic = Column(Boolean, default=False) 
    forest = Column(Boolean, default=False) 
    hill = Column(Boolean, default=False) 
    swamp = Column(Boolean, default=False) 
    cavern = Column(Boolean, default=False)

    map = relationship(Map, backref=backref('regions'))

    def __init__(self, defTokensNum, map_): 
        self.defTokensNum = defTokensNum
        self.map = map_

    def getState(self, gameId):
    	state = filter(lambda x : x.gameId == gameId, self.states)
    	if not state: raise BadFieldException('badGameId')
    	return state[0]

    def getNeighbors(self):
        return map(lambda x : x.left, self.rightNeighbors) + map(lambda x : x.right, self.leftNeighbors)

    def adjacent(self, region):
    	return region in self.getNeighbors() 


class Adjacency(Base):
	__tablename__ = 'adjacentRegions'

	leftId = Column(Integer, ForeignKey('regions.id'), primary_key=True)
	rightId = Column(Integer, ForeignKey('regions.id'), primary_key=True)
	mapId = Column(Integer, ForeignKey('maps.id'), primary_key=True)

   	left = relationship(Region, primaryjoin=leftId==Region.id, backref=backref('leftNeighbors'))
    	right = relationship(Region, primaryjoin=rightId==Region.id, backref=backref('rightNeighbors'))
	map = relationship(Map)

	def __init__(self, n1, n2):
      		self.leftId = n1
          	self.rightId = n2
        	

class RegionState(Base):
	__tablename__ = 'currentRegionStates'
	
    	id = pkey()
    	gameId = fkey('games.id')
	regionId = fkey('regions.id') 
    	tokenBadgeId = fkey('tokenBadges.id') 
    	ownerId = fkey('users.id')
    	tokensNum = Column(Integer, default = 0)
    	holeInTheGround = Column(Boolean, default = False)
    	encampment = Column(Integer, default = 0)
    	dragon = Column(Boolean, default = False) 
    	fortress = Column(Boolean, default = False) 
    	hero = Column(Boolean, default = False) 
    	fortified = Column(Boolean, default = False) 
    	inDecline = Column(Boolean, default = False) 

    	game = relationship(Game)
    	tokenBadge = relationship(TokenBadge, backref=backref('regions'))    # rename
    	owner = relationship(User, backref=backref('regions'))
    	region = relationship(Region, backref=backref('states'))

	def __init__(self, region, game):
		self.region = region
        	self.game = game
        	self.tokensNum = region.defTokensNum


	def clearFromRace(self, tokenBadge):
		callRaceMethod(tokenBadge.raceId, 'clearRegion', tokenBadge, self)
		callSpecialPowerMethod(tokenBadge.specPowerId, 'clearRegion', tokenBadge, self)

	def checkIfImmune(self):
		if self.holeInTheGround or self.dragon or self.hero:
			raise BadFieldException('regionIsImmune')

	def checkRegionIsCorrect(self, tokenBadge):
		if tokenBadge != self.tokenBadge:
			raise BadFieldException('badRegion')

class Message(Base):
    __tablename__ = 'chat'

    id = pkey()
    sender = fkey('users.id')
    text = Column(Text)
    time = Column(Integer)

    def __init__(self, sender, text, time): 
        self.sender = sender
        self.text = text
        self.time = time

class HistoryEntry(Base):
    __tablename__ = 'history'

    id = pkey()
    userId = fkey('users.id')
    gameId = fkey('games.id')
    state = Column(Integer)
    tokenBadgeId = Column(Integer)
    turn = Column(Integer)
    dice = Column(Integer)
    friend = Column(Integer)

    game = relationship(Game, backref=backref('history', order_by=id))
    user = relationship(User, backref=backref('history'))

    def __init__(self, userId, gameId, state, tokenBadgeId, dice = None): 
        self.userId = userId
        self.gameId = gameId
        self.state = state
        self.tokenBadgeId = tokenBadgeId
        self.dice = dice

class WarHistoryEntry(Base):
    __tablename__ = 'warHistory'

    id = pkey()
    mainHistEntryId = fkey('history.id')
    agressorBadgeId = fkey('tokenBadges.id')
    victimBadgeId = fkey('tokenBadges.id')
    conqRegionId = Column(Integer)
    victimTokensNum = Column(Integer, default = 0)
    diceRes = Column(Integer)
    attackType = Column(Integer) 
    
    mainHistEntry = relationship(HistoryEntry, backref=backref('warHistory', uselist=False))
    agressorBadge = relationship(TokenBadge, primaryjoin=agressorBadgeId==TokenBadge.id)
    victimBadge = relationship(TokenBadge, primaryjoin=victimBadgeId==TokenBadge.id)

  	

    def __init__(self, mainHistEntryId, agressorBadgeId, conqRegionId, victimBadgeId, victimTokensNum, diceRes, attackType): 
       self.mainHistEntryId = mainHistEntryId
       self.agressorBadgeId = agressorBadgeId
       self.conqRegionId = conqRegionId
       self.victimBadgeId = victimBadgeId
       self.diceRes = diceRes
       self.attackType = attackType
       self.victimTokensNum = victimTokensNum
       	



class _Database:
	engine = create_engine(DB_STRING, echo=True)


	def __init__(self):
		Base.metadata.create_all(self.engine)
		Session = sessionmaker(bind=self.engine)
		self.session = Session()

	def commit(self):
		self.session.commit()

	def rollback(self):
		self.session.rollback()

	def add(self, obj):
   		self.session.add(obj)
   		self.commit()

    	def addAll(self, objs):
    		self.session.add_all(objs)
    		self.commit()

    	def delete(self, *args, **kwargs):
    		self.session.delete(*args, **kwargs)
    		self.commit()

    	def query(self, *args, **kwargs):
    		return self.session.query(*args, **kwargs)

    	def clear(self):
    		meta = MetaData()
    		meta.reflect(bind=self.engine)
    		for table in reversed(meta.sorted_tables):
			self.engine.drop(table)
		Base.metadata.create_all(self.engine)

	def getXbyY(self, x, y, value, mandatory=True):
		try:
			cls = globals()[x]
			return self.query(cls).filter(getattr(cls, y) == value).one()
		except NoResultFound:
			if mandatory:    	
				n =  x + y[0].upper() + y[1:]
				raise BadFieldException("""bad%s""" % n)
			return None
   			

    	def addUnique(self, obj, name):
    		try:
    			self.add(obj)
    		except IntegrityError:
    			raise BadFieldException("""%sTaken""" % name)
    
    	def addRegion(self, map_, regInfo):
    		checkFields.checkListCorrectness(regInfo, 'landDescription', str)
    		checkFields.checkListCorrectness(regInfo, 'adjacent', int)
    		if not 'population' in regInfo:
    			regInfo['population'] = 0

        	reg = Region(regInfo['population'], map_)
        	self.add(reg)
        	for descr in regInfo['landDescription']:
        		if not descr in misc.possibleLandDescription[:11]:
        			raise BadFieldException('unknownLandDescription')
        		setattr(reg, descr, 1)

	def addNeighbors(self, reg, nodes):
		for node in nodes:
			node.map = reg.map
			self.add(node)

  
    	def getUserByNameAndPwd(self, username, password):
    		try:
    			return self.session.query(User).\
    				filter(User.name == username).\
    				filter(User.password == password).one()
    		except NoResultFound:
    			raise BadFieldException('badUsernameOrPassword')

    	def updateHistory(self, userId, gameId, state, tokenBadgeId, dice = None): 
    		self.add(HistoryEntry(userId,  gameId, state, tokenBadgeId, dice))

    	def updateWarHistory(	self, userId, gameId, victimBadgeId, agressorBadgeId, dice, regionId, defense, attackType):
    		hist = HistoryEntry(userId, gameId, misc.GAME_CONQUER, agressorBadgeId, dice)
    		self.add(hist)
    		self.add(WarHistoryEntry(hist.id, agressorBadgeId, regionId, victimBadgeId, defense, dice, attackType))


_database = _Database()


def Database():
    return _database


