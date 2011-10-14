from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_MAPNAME_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN
from gameExceptions import BadFieldException
from sqlalchemy import create_engine, and_, Table, Boolean, Column, Integer, String, MetaData, Date, ForeignKey, DateTime, Text, ForeignKeyConstraint
from sqlalchemy.orm import sessionmaker, relationship, backref, join
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

import misc
import checkFields
import sys
import json

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
		if not region: 
			raise BadFieldException('badRegionId')
		return region[0]

	def getRegions(self):
		return self.regions

class Game(Base):
	__tablename__ = 'games'

	id = pkey()
	name = uniqString(MAX_GAMENAME_LEN)
	descr = string(MAX_GAMEDESCR_LEN)
	state = Column(Integer)
	turn = Column(Integer, default=0)
	activePlayerId = Column(Integer)
	mapId = fkey('maps.id')

	map = relationship(Map)
	
	
	def __init__(self, name, descr, map): 
		self.name = name
		self.descr = descr
		self.state = misc.GAME_WAITING
		self.map = map

	def getTokenBadge(self, position):
		tokenBadge = filter(lambda x: x.pos == position, self.tokenBadges)
		if not tokenBadge: raise BadFieldException('badPosition')
		return tokenBadge[0]

	def checkStage(self, state, user, attackType = None):
		lastEvent = self.history[-1]
		badStage = not (lastEvent.state in misc.possiblePrevCmd[state]) 
		if attackType:
			curTurnHistory = filter(lambda x: x.turn == user.game.turn and 
				x.userId == user.id and x.state == misc.GAME_CONQUER, 
				user.game.history)
			if curTurnHistory:
				if filter(lambda x: x.warHistory.attackType == attackType, curTurnHistory):
					badStage = True
		if lastEvent.state == misc.GAME_CONQUER:
			battle = lastEvent.warHistory
			victim = battle.victimBadge
			canDefend = victim != None  and\
				not victim.inDecline and\
				battle.attackType != misc.ATTACK_ENCHANT and\
				battle.victimTokensNum > 1
			badStage |= (canDefend != (state == misc.GAME_DEFEND)) or (state == misc.GAME_DEFEND and user.currentTokenBadge != victim)
		if badStage or (user.id != self.activePlayerId and state != misc.GAME_DEFEND):
			raise BadFieldException('badStage')

	def getDefendingRegion(self, player):
		lastWarHistoryEntry = self.history[-1].warHistory
		return lastWarHistoryEntry.conqRegion.region


	def clear(self):
		tables = ['Games', 'TokenBadges', 'CurrentRegionState', 'History', 'GameHistory', 'WarHistory']
		for table in tables:
			self.engine.execute("DELETE FROM %s WHERE GameId=%s", table, id)
		for table in tables:
			self.engine.execute("ALTER TABLE %s AUTO_INCREMENT=1", table)

	def getLastState(self):
		return self.history[-1].state


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
    	specPowNum = Column(Integer, default = 0)

    	game = relationship(Game, backref=backref('tokenBadges'))

 	def __init__(self, raceId, specPowId, gameId): 
 		self.raceId = raceId
        	self.specPowId = specPowId
        	self.gameId = gameId

        def isNeighbor(self, region):
         	for reg in self.regions:
        		if region.adjacent(reg.region):
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
	currentTokenBadge = relationship(TokenBadge, backref=backref('owner', uselist=False), 
	primaryjoin=currentTokenBadgeId==TokenBadge.id)
	declinedTokenBadge = relationship(TokenBadge, primaryjoin=declinedTokenBadgeId==TokenBadge.id)

	def __init__(self, username, password):
		self.name = username
		self.password = password

	def checkForFriends(self, attackedUser):			
		if not attackedUser: return
		turn = self.game.turn - int(self.priority < attackedUser.priority) 
		histEntry = filter(lambda x : x.turn == turn and x.state == misc.GAME_CHOOSE_FRIEND and\
			x.userId == attackedUser.id, self.game.history)
		if histEntry:
			print histEntry[0].friend, attackedUser.id
			if histEntry[0].friend == self.id:
				raise BadFieldException('usersAreFriends')

	def killRaceInDecline(self):
		for declinedRegion in self.declinedTokenBadge.regions:
			declinedRegion.owner = None
			declinedRegion.inDecline = False
	
	def getNonEmptyConqueredRegions(self):
		conqHist = filter(lambda x: x.turn == self.game.turn and x.state == misc.GAME_CONQUER, self.game.history)
		return len(filter(lambda x: x.warHistory.conqRegion.tokensNum > 0,  conqHist))

class Region(Base):
	__tablename__ = 'regions'

	id = Column(Integer, primary_key=True, autoincrement=False)
	mapId =  Column(Integer, ForeignKey('maps.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
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

	map = relationship(Map, backref=backref('regions', order_by=id))
	neighbors = relationship('Adjacency'  ,primaryjoin='and_(Region.id==Adjacency.regId,\
		 Region.mapId==Adjacency.mapId)')

	def __init__(self, id, defTokensNum, map_): 
		self.id = id
		self.defTokensNum = defTokensNum
		self.map = map_

	def getState(self, gameId):
		state = filter(lambda x : x.gameId == gameId, self.states)
		if not state: raise BadFieldException('badGameId')
		return state[0]

	def getNeighbors(self):
		return  map(lambda x : x.neighborId, self.neighbors) 

	def adjacent(self, region):
		return region.id in self.getNeighbors() 

class RegionState(Base):
	__tablename__ = 'currentRegionStates'
	
	id = pkey()
	gameId = fkey('games.id')
	tokenBadgeId = fkey('tokenBadges.id') 
	ownerId = fkey('users.id')
	regionId = Column(Integer, default = 0)
	mapId  = Column(Integer, default = 0)		# Would get rid of this but don't know how
	tokensNum = Column(Integer, default = 0)
	holeInTheGround = Column(Boolean, default = False)
	encampment = Column(Integer, default = 0)
	dragon = Column(Boolean, default = False) 
	fortress = Column(Boolean, default = False) 
	hero = Column(Boolean, default = False) 
	inDecline = Column(Boolean, default = False) 

	game = relationship(Game)
	tokenBadge = relationship(TokenBadge, backref=backref('regions'))    # rename
	owner = relationship(User, backref=backref('regions'))
	region = relationship(Region, backref=backref('states'))

	__table_args__ = (ForeignKeyConstraint([regionId, mapId], [Region.id, Region.mapId]), {})

	def __init__(self, region, game):
		self.region = region
		self.game = game
		self.tokensNum = region.defTokensNum


	def checkIfImmune(self, enchanting=False):
		if self.holeInTheGround or self.dragon or self.hero:
			raise BadFieldException('regionIsImmune')
		if enchanting:
			if self.encampment: raise BadFieldException('regionIsImmune')
			if not self.tokensNum: 	raise BadFieldException('nothingToEnchant')
			if self.tokensNum > 1: 	raise BadFieldException('cannotEnchantMoreThanOneToken')
			if self.inDecline: raise BadFieldException('cannotEnchantDeclinedRace')


class Adjacency(Base):
	__tablename__ = 'adjacentRegions'

	regId = Column(Integer, ForeignKey('regions.id'), primary_key=True)
	neighborId = Column(Integer, ForeignKey('regions.id'), primary_key=True)
	mapId = Column(Integer, ForeignKey('regions.mapId'), primary_key=True)


	def __init__(self, n1, n2):
		self.regId = n1
		self.neighborId = n2


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

	def __init__(self, user, state, tokenBadgeId, dice = None, friend = None): 
		self.userId = user.id
		self.gameId = user.game.id
		self.state = state
		self.tokenBadgeId = tokenBadgeId
		self.dice = dice
		self.turn = user.game.turn
		self.friend = friend

class GameHistoryEntry(Base):
	__tablename__ = 'gameHistory'

	id = pkey()
	gameId = fkey('games.id')
	action = Column(Text)

	game = relationship(Game, backref=backref('gameHistory', order_by=id))

	def __init__(self, game, action): 
		self.gameId = game.id
		self.action = action

class WarHistoryEntry(Base):
	__tablename__ = 'warHistory'

	id = pkey()
	mainHistEntryId = fkey('history.id')
	agressorBadgeId = fkey('tokenBadges.id')
	victimBadgeId = fkey('tokenBadges.id')
	conqRegionId = fkey('currentRegionStates.id')
	victimTokensNum = Column(Integer, default = 0)
	diceRes = Column(Integer)
	attackType = Column(Integer) 

	mainHistEntry = relationship(HistoryEntry, backref=backref('warHistory', uselist=False))
	agressorBadge = relationship(TokenBadge, primaryjoin=agressorBadgeId==TokenBadge.id)
	victimBadge = relationship(TokenBadge, primaryjoin=victimBadgeId==TokenBadge.id)
	conqRegion = relationship(RegionState, uselist=False)

	def __init__(self, mainHistEntryId, agressorBadgeId, conqRegionId, victimBadgeId, victimTokensNum, diceRes, attackType): 
		self.mainHistEntryId = mainHistEntryId
		self.agressorBadgeId = agressorBadgeId
		self.conqRegionId = conqRegionId
		self.victimBadgeId = victimBadgeId
		self.diceRes = diceRes
		self.attackType = attackType
		self.victimTokensNum = victimTokensNum

class _Database:
	engine = create_engine(DB_STRING, echo=False)


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
		#	self.engine.execute("ALTER TABLE %s AUTO_INCREMENT=0" % table.name)
		#	if misc.TEST_MODE and table.name !=  'adjacentregions' and table.name !=  'maps' and table.name != 'regions':
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

	def getNextPlayer(self, game):
		try:
			activePlayer = self.query(User).get(game.activePlayerId)
			return self.query(User).filter(User.priority > activePlayer.priority).one()
		except NoResultFound:
			return None


	def addUnique(self, obj, name):
		try:
			self.add(obj)
		except IntegrityError:
			raise BadFieldException("""%sTaken""" % name)
    
	def addRegion(self, id, map_, regInfo):
		checkFields.checkListCorrectness(regInfo, 'landDescription', str)
		checkFields.checkListCorrectness(regInfo, 'adjacent', int)
		if not 'population' in regInfo:
			regInfo['population'] = 0

		reg = Region(id, regInfo['population'], map_)
		self.add(reg)
		for descr in regInfo['landDescription']:
			if not descr in misc.possibleLandDescription[:11]:
				raise BadFieldException('unknownLandDescription')
			setattr(reg, descr, 1)

	def addNeighbors(self, reg, nodes):
		for node in nodes:
			node.mapId = reg.mapId
			self.add(node)

  
	def getUserByNameAndPwd(self, username, password):
		try:
			return self.session.query(User).\
				filter(User.name == username).\
				filter(User.password == password).one()
		except NoResultFound:
			raise BadFieldException('badUsernameOrPassword')

	def updateHistory(self, user, state, tokenBadgeId, dice = None, friend=None): 
		self.add(HistoryEntry(user, state, tokenBadgeId, dice, friend))

	def updateGameHistory(self, game, data):
		if 'sid' in data:
			user = self.getXbyY('User', 'sid', data['sid'])
			del data['sid']
			data['userId'] = user.id
		self.add(GameHistoryEntry(game, json.dumps(data)))

	def updateWarHistory(self, user, victimBadgeId, agressorBadgeId, dice, regionId, 
		defense, attackType):
		hist = HistoryEntry(user, misc.GAME_CONQUER, agressorBadgeId, dice)
		self.add(hist)
		self.add(WarHistoryEntry(hist.id, agressorBadgeId, regionId, victimBadgeId, 
			defense, dice, attackType))


_database = _Database()


def Database():
    return _database


