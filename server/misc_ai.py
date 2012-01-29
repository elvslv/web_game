from Queue import Queue as Queue
import math
import itertools


REDEPLOYMENT_CODE = 4
HERO_CODE = 5
FORTRESS_CODE = 6
ENCAMPMENTS_CODE = 7

		
def distributeUnits(regions, unitsNum, req):
	sum = reduce(lambda x, y: x + y, map(lambda x: x.needDef, regions))
	unitsRest = unitsNum
	for reg in regions:
		share = math.floor(unitsNum * (float(reg.needDef) / sum))
		if not share: break
		else: unitsRest -= int(share)
		req[reg.id] += int(share) 
	if unitsRest:
		priorityRegs=filter(lambda x: x.needDef ==(max(regions, key=lambda x: x.needDef)).needDef, regions)
		(div, mod) = divmod(unitsRest, len(priorityRegs))
		if div:
			for region in priorityRegs: 
				req[region.id] += div
		if mod:
			for region in priorityRegs:
				mod -= 1
				req[region.id] += 1
				if not mod: break

def generateRegionCombinations(regionIds):
	r = list()
	for i in range(1, 7):
		r += list(itertools.combinations(regionIds, i))
	return r


def mList(el):
	a = list()
	a.append(el)
	return a


def convertStrategy(strat, sid):
	res = []
	useDragon = False
	useEnchantment = False
	for el in strat:
		if el == 'e':
			useEnchantment = True
		elif el == 'd':
			useDragon = True
		else:
			act = None
			if useDragon:
				act = 'dragonAttack'
				useDragon = False
			elif useEnchantment:
				act = 'enchant'
				useEnchantment = False
			else:
				act = 'conquer'
			res.append({'action' : act, 'sid' : sid, 'regionId' : el.id})
	print res
	return res

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
	return res[0] if code == FORTRESS_CODE else res
		
	