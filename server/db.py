from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MAX_MAPNAME_LEN, MAX_GAMENAME_LEN, MAX_GAMEDESCR_LEN
from gameExceptions import BadFieldException
from sqlalchemy import create_engine, Table, Boolean, Column, Integer, String, MetaData, Date, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref, join
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

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
    activePlayer = Column(Integer)
    mapId = fkey('maps.id')

    map = relationship(Map)

    def __init__(self, name, descr, turn, mapId): 
        self.name = name
        self.descr = descr
        self.turn = turn
        self.mapId = mapId

class User(Base):
    __tablename__ = 'users'

    id = pkey()
    name = Column(String(MAX_USERNAME_LEN), unique=True, nullable=False)
    password = string(MAX_PASSWORD_LEN)
    sid = Column(Integer, unique=True)
    gameId = fkey('games.id')
    isReady = Column(Boolean, default=False)
    currentTokenBadge = Column(Integer)
    declinedTokenBadge = Column(Integer) 
    coins = Column(Integer)
    tokensInHand = Column(Integer, default = 0)
    priority = Column(Integer)

    game = relationship(Game, backref=backref('players'))

    def __init__(self, username, password):
        self.name = username
        self.password = password


class TokenBadge(Base):
    __tablename__ = 'tokenBadges'

    id = pkey()
    raceId = Column(Integer)
    specPowId = Column(Integer)
    gameId = fkey('games.id')
    ownerId = fkey('users.id')
    pos = Column(Integer)
    bonusMoney = Column(Integer, default = 0)
    inDecline = Column(Boolean, default=False)
    totalTokensNum = Column(Integer, default = 0)
    totalSpecPowerBonusNum = Column(Integer, default = 0)

    game = relationship(Game, backref=backref('tokenBadges'))
    owner = relationship(User, backref=backref('tokenBadges'))

    def __init__(self, raceId, specPowerId): 
        self.raceId = raceId
        self.specPowerId = specPowerId

class Region(Base):
    __tablename__ = 'regions'

    id = pkey()
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

    def __init__(self, defTokensNum, descr): 
        self.defTokensNum = defTokensNum
        self.descr = descr

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
    left = relationship(Region, primaryjoin=leftId==Region.id, backref=backref('leftNeighbors'))
    right = relationship(Region, primaryjoin=rightId==Region.id, backref=backref('rightNeighbors'))

    def __init__(self, n1, n2):
        if n1.id < n2.id:
            self.left = n1
            self.right = n2
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
    tokenBadge = relationship(TokenBadge, backref=backref('ourRegionState'))    # rename
    owner = relationship(User, backref=backref('regions'))
    region = relationship(Region, uselist=False, backref=backref('state'))

    def __init__(self, regionId):
        self.regionId = regionId

class Message(Base):
    __tablename__ = 'chat'

    id = pkey()
    sender = fkey('users.id')
    text = string(300)
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

    game = relationship(Game, backref=backref('history'))
    user = relationship(User, backref=backref('history'))

    def __init__(self, userId, gameId, state, tokenBadgeId): 
        self.userId = userId
        self.gameId = gameId
        self.state = state
        self.tokenBadgeId = tokenBadgeId

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
    agressorBadge = relationship(TokenBadge, primaryjoin=aggressorBadgeId==TokenBadge.id)
    victimBadge = relationship(TokenBadge, primaryjoin=victimBadgeId==TokenBadge.id)

    def __init__(self, mainHistEntry, aggressorBadgeId, conqRegion, victimBadgeId, diceRes, attackType): 
       self.mainHistEntry = mainHistoryEntry
       self.aggressorBadgeId = aggressorBadgeId
       self.conqRegion = conqRegion
       self.victimBadgeId = victimBadgeId
       self.diceRes = diceRes
       self.attackType = attackType


class _Database:
    engine = create_engine(DB_STRING, echo=True)

    def __init__(self):
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def addUser(self, user):
        try:
            self.add(user)
        except IntegrityError:
            self.rollback()
            raise BadFieldException('UsernameTaken')

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
        for table in Base.metadata.sorted_tables:
            self.engine.execute(table.delete())

    def getUserBySid(self, sid):
        try:
            return self.session.query(User).filter_by(sid=sid).one()
        except NoResultFound:
          return None
    
    def getUserByNameAndPwd(self, username, password):
        try:
            return self.session.query(User).\
                filter(User.name == username).\
                filter(User.password == password).one()
        except NoResultFound:
            return None


_database = _Database()

def Database():
    return _database


if __name__=='__main__':
	a = Database()
