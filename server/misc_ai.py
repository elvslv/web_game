from Queue import Queue as Queue

REDEPLOYMENT_CODE = 4
HERO_CODE = 5
FORTRESS_CODE = 6
ENCAMPMENTS_CODE = 7


def calcDistances(user, regions):
	alwaysZeroDist = user.canBeAttackedFromOutsideTheMap()
	for region in regions:
		if alwaysZeroDist and region.border:
			region.distFromEnemy = 1
			continue				
		q = Queue()
		cur = None
		dist = 0
		q.put(region)
		region.visited = True		
		stop = False		
		while not (q.empty() or stop):			
			cur = q.get()
			for reg in cur.adjacent:
				if reg.visited: continue
				if reg.ownerId and not reg.inDecline and reg.ownerId != user.id:
					stop = True
					break
				reg.visited = True
				q.put(reg)
			dist += 1
		region.distFromEnemy = dist
	print map(lambda x: (x.distFromEnemy, x.id), regions)

def distributeUnits(regions, unitsNum, req):
	if unitsNum:
		(div, mod) = divmod(unitsNum, len(regions))
		if div:
			for region in regions: req[region.id] += div
		if mod:
			for region in regions:
				mod -= 1
				req[region.id] += 1
				if not mod: break


def convertRedeploymentRequest(req, code):
	nextRecMaker = {
		REDEPLOYMENT_CODE : lambda x: {'regionId' : x[0], 'tokensNum' : x[1]},
		HERO_CODE : lambda x: {'regionId' : x[0]},
		FORTRESS_CODE :  lambda x: {'regionId' : x[0]},
		ENCAMPMENTS_CODE : lambda x: {'regionId' : x[0], 'encampmentsNum' : x[1]}
	}[code]
	res = []
	for rec in req.items():
		res.append(nextRecMaker(rec))
	print res
	return res[0] if code == FORTRESS_CODE else res
		
	