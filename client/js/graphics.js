var paths = {
	"forest" : "css/images/forest.jpg",
	"swamp" : "css/images/swamp.jpg",
	"sea" : "css/images/sea.jpg",
	"hill" : "css/images/hill.jpg",
	"mountain" : "css/images/mountain.jpg",
	"farmland" : "css/images/farmland.jpg",
	"magic" : "css/images/magic.jpg",
	"cavern" : "css/images/cavern.jpg",
	"mine" : "css/images/mine.jpg",
	"natives" : "css/images/races/elves small.jpg"
};

Graphics = {};

Graphics.colors = [];

Graphics.forbidUpdate = function(){
	return !game() || game().redeployStarted || 
		game().defendStarted || Graphics.dragging;
};

Graphics.freeTokens = {
	raceCoords : [60, 550],
	powerCoords : [270, 550],
	ui : {}
};

Graphics.drawTokenBadge = function(reg, badgeType, num){	
	if (!num) return;
	var pic = badgeType.getPic(reg !== null && reg.inDecline),
		place = reg || Graphics.freeTokens,
		coords = badgeType.race ? place.raceCoords : place.powerCoords,
		previousBadge = badgeType.race ? place.ui.race : place.ui.power,
		badge; 

//	console.log(previousBadge);
	if (previousBadge) {
		previousBadge.remove();
		delete previousBadge;
	}
	badge = Graphics.paper.rect(coords[0], coords[1], 50, 50)
				.attr({fill : "url(" + pic +")"}).toFront();
	badge.num = Graphics.paper.text(coords[0] + 36, coords[1] + 14, num)
		.attr({"font": '100 14px "Helvetica Neue", Helvetica', "fill" : "red",
			"text-anchor": "start"}).toFront();
	badge.num.n = num;
	badge.canDrag = (function(badgeType){
		return function(){
			return (!reg || (reg.ownerId === user().id && !reg.inDecline)) && 
				((game().defendStarted && !badgeType.power && !reg) ||
				(game().redeployStarted && badgeType.canStartRedeploy(reg)) ||
				(badgeType.name === 'DragonMaster'));
		};	
	}(badgeType));
	
	badge.drag(
		function(dx, dy){
			if (!this.canDrag()) return;
			this.attr({x: this.ox + dx, y: this.oy + dy}); 
			this.num.attr({x: this.num.ox + dx, y: this.num.oy + dy}); 
		
		},
		function(){
			if (!this.canDrag()) return;
			Graphics.dragging = true;
			if (this.num.n > 1) {
				this.tempCopy = this.clone();
				this.tempCopy.num = this.num.clone();
				this.tempCopy.num.attr({"text" : this.num.n - 1});
				this.num.attr({"text" : 1});
			} 
			this.ox = this.attr("x");
			this.oy = this.attr("y");
			this.num.ox = this.num.attr("x");
			this.num.oy = this.num.attr("y");
			this.toFront();
			this.num.toFront();
		},
		function(){
			if (!this.canDrag()) return;
			var offset = Graphics.offset(),
				posX = this.getBBox().x + offset.left,
				posY = this.getBBox().y + offset.top,
				element = Graphics.paper.getElementByPoint(posX, posY),
				newRegion, 
				that = this,
				last = function(){
					return !that.tempCopy;
				},	
				restore = function(){
					that.num.attr({"text" : that.num.n});
					that.attr({x: that.ox, y: that.oy}); 
					that.num.attr({x: that.num.ox, y: that.num.oy});
				}, 
				deleteBadge = function(reg){
					if (reg){
						if (badgeType.race) reg.ui.race = undefined;
						else reg.ui.power = undefined;
					}
					that.num.remove();
					that.remove();
				},
				onSuccess = function(oldRegion, newRegion){
					badgeType.onDropSuccess(oldRegion, newRegion);
					if (!last()) {
						that.num.n--;
						restore();
					} else 
						deleteBadge(oldRegion);
				};
				
			if (element) newRegion = element.r ? element.r : element; 
			
			if (newRegion && newRegion.model &&	
					newRegion.canDrop(badgeType) && 
					(!reg || newRegion.model.id !== reg.id))

				onSuccess(reg, newRegion.model);
			else restore(); 

			if (!last()) {
				this.tempCopy.remove();
				delete this.tempCopy;
			}
			Graphics.dragging = false;
		});
	if (reg){
		if (badgeType.race) reg.ui.race = badge;
		else reg.ui.power = badge;
		badge.r = reg.ui;
	}
	return badge;
};

Graphics.offset = function(){
	var br = $.browser, left, top;
	if (br.opera || br.webkit) { 
		left = Graphics.paper.canvas.offsetLeft;
		top = Graphics.paper.canvas.offsetTop;
	} else{
		left = $(Graphics.paper.canvas).offset().left;
		top = $(Graphics.paper.canvas).offset().top;
	}
	return {
			left : left - $(document).scrollLeft(),		//check again 
			top : top - $(document).scrollTop()
	};						
};							

Graphics.getRegColor = function(region){
	return region.ownerId ? Graphics.colors[region.ownerId] : "silver";
};

Graphics.getRegBoundsColor = function(region){
	return	region.conquerable ? "yellow" : 
		canBeginDefend() && canDefend(region) ? "fuchsia" : "black";
};

Graphics.drawRegionBadges = function(region){
	var tBadge = region.getTokenBadge();
	Graphics.drawTokenBadge(region, tBadge ? tBadge.getRace() : getBaseRace(), 
			region.tokensNum);
	if (tBadge && tBadge.getPower().needRendering())
		Graphics.drawTokenBadge(region, tBadge.getPower(), 
			0 + region[tBadge.getPower().regPropName]);
};

Graphics.drawFreeBadges = function(){
	Graphics.freeTokens.ui.race = Graphics.drawTokenBadge(null, user().race(), user().freeTokens);
	Graphics.freeTokens.ui.power = Graphics.drawTokenBadge(null, user().specPower(), user().freePowerTokens);
};	

Graphics.update = function(map){
	if (Graphics.forbidUpdate()) return;
	var cur, i
	for (i = 0; i < map.regions.length; ++i){
		cur = map.regions[i];
		cur.ui.animate({fill : Graphics.getRegColor(cur)}, 1000);
		cur.ui.attr({"stroke" : Graphics.getRegBoundsColor(cur)});
		Graphics.drawRegionBadges(cur);
	}
	Graphics.drawFreeBadges();
};

Graphics.assignColors = function(){
	if (Graphics.colors.length) return;
	var i;
	for (i = 0; i < game().players.length; i++) 
		Graphics.colors[game().players[i].id] = Raphael.getColor();
};

		
Graphics.drawMap = function(map) {
	Graphics.paper = Raphael("map", 630, 620);
	var paper = Graphics.paper,
		selectRegion = function(reg, sel){
			return function(){
				reg.animate({stroke: sel ? "red" : 
					Graphics.getRegBoundsColor(reg.model)}, 300);
				if (!Graphics.dragging)
					reg.toFront();
				if (reg.race) {
					reg.race.toFront();
					reg.race.num.toFront();
				}
				if (reg.power) {
					reg.power.toFront();
					reg.power.num.toFront();
				}
			}
		},
		drawRegion = function(region){
			var fillStyle = Graphics.getRegColor(region),
			strokeStyle = Graphics.getRegBoundsColor(region),
			r = paper.path(getSvgPath(region.coords))
				.attr({fill: fillStyle, stroke : strokeStyle,
				"stroke-width": 3, "stroke-linecap": "round"});
			region.ui = r;
			r.model = region;
			Graphics.drawRegionBadges(region);
			r.hover(selectRegion(r, true), selectRegion(r, false));
			r.click(regionClick(region));
			r.canDrop = function(badgeType){
				if (game().redeployStarted || badgeType.name === 'DragonMaster')
					return badgeType.canDrop(region);						
				else
					return badgeType.race && canDefend(region);
		};
		r.addUnit = function(badgeType){
			var field = badgeType.race ? 'race' : 'power';
			if (!this[field]) 
				Graphics.drawTokenBadge(region, badgeType, 1)
			else {
				this[field].num.n++;
				this[field].num.attr({"text" : this[field].num.n});
			}
		};
		return r;
	};
	for (var i = 0; i < map.regions.length; ++i)
		drawRegion(map.regions[i]);
	var frame = paper.rect(0, 515, 630, 105).attr({fill: "LightYellow", stroke: "black"});
	Graphics.drawFreeBadges();

};
	
