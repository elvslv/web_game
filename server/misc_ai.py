from Queue import Queue as Queue

REDEPLOYMENT_CODE = 4
HERO_CODE = 5
FORTRESS_CODE = 6
ENCAMPMENTS_CODE = 7


		
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
	return res[0] if code == FORTRESS_CODE else res
		
	