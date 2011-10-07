from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_MAPNAME_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN
from gameExceptions import BadFieldException
from sqlalchemy import create_engine, Table, Boolean, Column, Integer, String, MetaData, Date, ForeignKey, DateTime, Text
from sqlalchemy.orm import sessionmaker, relationship, backref, join
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

import misc

DATABASE_HOST = "localhost"
DATABASE_USER = "admin"
DATABASE_NAME = "testdb"
DATABASE_PASSWD = "12345"
DATABASE_PORT = 3306

DB_STRING =  """mysql+mysqldb://%s:%s@%s:%d/%s""" % \
	(DATABASE_USER, DATABASE_PASSWD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME)


Base = declarative_base()

string = lambda len: Column(String(len))
pkey = lambda: Column(Integer, primary_key=True)
fkey = lambda name: Column(Integer, ForeignKey(name, onupdate='CASCADE', ondelete='CASCADE'))
requiredInteger = lambda: Column(Integer, nullable=False)


class Map(Base):
	__tablename__ = 'maps'

	id = pkey()
    	name = string(MAX_MAPNAME_LEN)
   	playersNum = Column(Integer)
    	turnsNum = Column(Integer)
    
    	def __init__(self, name, playersNum, turnsNum): 
    		self.name = name
    		self.playersNum = playersNum
    		self.turnsNum = turnsNum

class Game(Base):
	__tablename__ = 'games'

    	id = pkey()
    	name = string(MAX_GAMENAME_LEN)
    	descr = string(MAX_GAMEDESCR_LEN)
    	state = Column(Integer, default = 0)
    	turn = Column(Integer)
    	mapId = fkey('maps.id')
    	activePlayerId = fkey('users.id')

    	map = relationship(Map)
    	activePlayer = relationship(User)

    	def __init__(self, name, descr, mapId): 
    		self.name = name
        	self.descr = descr
        	self.turn = 0
        	self.state = GAME_WAITING
        	self.mapId = mapId

        

        def checkStage(self, state, user):
        	lastEvent = history[-1]
		aggressor = lastEvent.warHistory.aggressorBadge
        	war = aggressor and not agressor.tokenBadge.inDecline
        	if not lastEvent.state in misc.possiblePrevCmd[state] or 
        		war != state == GAME_DEFEND  or 
        		user != self.activePlayer:
        		
        		raise BadFieldException('badStage')

       def getDefendingRegionInfo(self, player):
       	lastWarHistoryEntry = self.warHistory[-1]
		if lastWarHistoryEntry.victimBadge.id != player.currentTokenBadge.id
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
			newActPlayer.tokensInHand += addUnits -len(newActPlayer.regions) + newActPlayer.currentTokenBadge.totalTokensNum)
			for region in newActPlayer.regions:
				region.tokensNum = 1

	def getNonEmptyConqueredRegions(self, tokenBadge):
		return len(filter(lambda x: x.agressorBadge == tokenBadge and agressorTokensNum > 0, warHistory))
        
class User(Base):
	__tablename__ = 'users'

    	id = pkey()
    	name = Column(String(MAX_USERNAME_LEN), unique=True, nullable=False)
    	password = string(MAX_PASSWORD_LEN)
    	sid = Column(Integer, unique=True)
    	gameId = fkey('games.id')
    	isReady = Column(Boolean, default=False)
    	currentTokenBadgeId = fkey('tokenBadges.id')
    	declinedTokenBadgeId = fkey('tokenBadges.id')
    	coins = Column(Integer, default=misc.INIT_COINS_NUM)
    	tokensInHand = Column(Integer, default = 0)
	priority = Column(Integer)

	
    	game = relationship(Game, backref=backref('players', order_by=priority))
    	currentTokenBadge = relationship(TokenBadge, backref=backref('owner'), primary_join=currentTokenBadgeId==TokenBadge.id)
    	declinedTokenBadge = relationship(TokenBadge, backref=backref('owner'), primary_join=declinedTokenBadgeId==TokenBadge.id)

    	def __init__(self, username, password):
       	self.name = username
        	self.password = password

        def checkForFriends(self, attackedUser):
		turn = self.game.turn -  int(self.priority < attackedUser.priority)
		histEntry = dbi.query(HistoryEntry).filter(HistoryEntry.id==self.game.id).\
									filter(HistoryEntry.turn==turn)
		if histEntry.state == GAME_CHOOSE_FRIEND and histEntry.user == self 
			and histEntry.friend == attackedUser:

			raise BadFieldException('UsersAreFriends')
			
class TokenBadge(Base):
    __tablename__ = 'tokenBadges'

    id = pkey()
    raceId = Column(Integer)
    specPowId = Column(Integer)
    gameId = fkey('games.id')
    pos = Column(Integer, default=0)
    bonusMoney = Column(Integer, default = 0)
    inDecline = Column(Boolean, default=False)
    totalTokensNum = Column(Integer, default = 0)

    game = relationship(Game, backref=backref('tokenBadges'))

    def __init__(self, raceId, specPowerId, gameId): 
        self.raceId = raceId
        self.specPowerId = specPowerId
        self.gameId = gameId

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

    def addNeighbors(self, *nodes):
        for node in nodes:
            Edge(self, node)
        return self
   
    def getNeighbors(self):
        return map(lambda x : x.left, self.rightNeightbors) + map(lambda x : x.right, self.leftNeightbors)


class Adjacency(Base):
	__tablename__ = 'adjacentRegions'

	leftId = Column(Integer, ForeignKey('regions.id'), primary_key=True)
	rightId = Column(Integer, ForeignKey('regions.id'), primary_key=True)
	mapId = Column(Integer, ForeignKey('maps.id'), primary_key=True)

   	left = relationship(Region, primaryjoin=leftId==Region.id, backref=backref('leftNeighbors'))
    	right = relationship(Region, primaryjoin=rightId==Region.id, backref=backref('rightNeighbors'))
	map_ = relationship(Map)

	def __init__(self, n1, n2):
		if n1.id < n2.id:
            		self.left = n1
            		self.right = n2
            		self.map = n1.map
		else:
            		self.left = n2
            		self.right = n1
        	

class RegionState(Base):
	__tablename__ = 'currentRegionStates'
	
    	id = pkey()
    	gameId = fkey('games.id')
    	tokenBadgeId = fkey('tokenBadges.id') 
    	ownerId = fkey('users.id')
    	regionId = fkey('regions.id') 
    	tokensNum = Column(Integer, default = 0)
    	holeInTheGround = Column(Boolean, default = False)
    	encampment = Column(Integer, default = 0)
    	dragon = Column(Boolean, default = False) 
    	fortress = Column(Boolean, default = False) 
    	hero = Column(Boolean, default = False) 
    	fortified = Column(Boolean, default = False) 
    	inDecline = Column(Boolean, default = False) 

    	game = relationship(Game, backref=backref('currentRegionState'))
    	tokenBadge = relationship(TokenBadge, backref=backref('regions'))    # rename
    	owner = relationship(User, backref=backref('regions'))
    	region = relationship(Region, uselist=False, backref=backref('state'))

	def __init__(self, regionId, gameId, tokensNum):
       	self.regionId = regionId
        	self.gameId = gameId
        	self.tokensNum = tokensNum

	def clearFromRace(self, tokenBadge):
		callRaceMethod(tokenBadge.raceId, 'clearRegion', tokenBadge.id, self.id)
		callSpecialPowerMethod(tokenBadge.specPowerId, 'clearRegion', tokenBadge.id, self.id)

	def checkIfImmune(self):
		if self.holeInTheGround or self.dragon or self.hero:
			raise BadFieldException('regionIsImmune')

	def checkRegionIsCorrect(self, tokenBadge):
		if tokenBadge != self.tokenBadge
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

class AttackingHistoryEntry(Base):
    __tablename__ = 'warHistory'

    id = pkey()
    mainHistEntryId = fkey('history.id')
    aggressorBadgeId = fkey('tokenBadges.id')
    victimBadgeId = fkey('tokenBadges.id')
    conqRegion = Column(Integer)
    aggressorTokensNum = Column(Integer, default = 0)
    diceRes = Column(Integer)
    attackType = Column(Integer) 
    
    mainHistEntry = relationship(HistoryEntry, backref=backref('warHistory'))
    agressorBadge = relationship(TokenBadge, primaryjoin=aggressorBadgeId==TokenBadge.id, backref=backref('tokenBadge')
    victimBadge = relationship(TokenBadge, primaryjoin=victimBadgeId==TokenBadge.id, backref=backref('TokenBadge'))

    def __init__(self, mainHistEntry, aggressorBadgeId, conqRegion, victimBadgeId, diceRes, attackType): 
       self.mainHistEntry = mainHistoryEntry
       self.aggressorBadgeId = aggressorBadgeId
       self.conqRegion = conqRegion
       self.victimBadgeId = victimBadgeId
       self.diceRes = diceRes
       self.attackType = attackType



class _Database:
    engine = create_engine(DB_STRING, echo=False)

    def __init__(self):
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def addUnique(self, obj, name):
        try:
            self.add(obj)
        except IntegrityError:
            self.rollback()
            raise BadFieldException("""%sTaken""" % name)
    
    def addRegion(map_, regInfo):
        misc.checkListCorrectness(regInfo, 'landDescription', str)
        misc.checkListCorrectness(regInfo, 'adjacent', int)
        if not 'population' in regInfo:
            regInfo['population'] = 0

        reg = Region(regInfo['population'], map_)
        for descr in regInfo['landDescription']:
            if not descr in misc.possibleLandDescription[:11]:
                raise BadFieldException('unknownLandDescription')
            setattr(reg, descr, 1)
        reg.addNeighbors(map(lambda x: Adjacency(reg.id, x), regInfo['adjacent'])).\
            addNeighbors(map(lambda x: Adjacency(x, reg.id), regInfo['adjacent'])) 

        self.add(reg)

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
        for table in meta.sorted_tables:
        	self.engine.execute(table.delete())
           

    def getUserBySid(self, sid, mandatory=True):
        try:
            return self.session.query(User).filter_by(sid=sid).one()
        except NoResultFound:
            if mandatory:
                raise BadFieldException('badSid')
            return None
    
    def getUserByNameAndPwd(self, username, password):
        try:
            return self.session.query(User).\
                filter(User.name == username).\
                filter(User.password == password).one()
        except NoResultFound:
           raise BadFieldException('badUsernameOrPassword')

## Are there any macro in python? 

    def getMapById(self, id):
        try:
            return self.session.query(Map).filter_by(id=id).one()
        except NoResultFound:
          return None
    
    def getGameById(self, id):
        try:
            return self.session.query(Game).filter_by(id=id).one()
        except NoResultFound:
          return None

	def getTokenBadgeByPosition(self, pos):
		try:
			return self.session.query(TokenBadge).filter_by(pos=pos).one()
		except NoResultFound:
			raise BadFieldException('badTokenBadgePosition')

	def getTokenBadgeById(self, pos):
		try:
			return self.session.query(TokenBadge).filter_by(id=id).one()
		except NoResultFound:
			raise BadFieldException('badTokenBadgeId')

	def getCurrentRegionStateById(self, id):
		try:
			return self.session.query(RegionState).filter_by(id=id).one()
		except NoResultFound:
			raise BadFieldException('badRegionStateId')



_database = _Database()

def Database():
    return _database
