from Queue import Queue as Queue
import math

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
		
	