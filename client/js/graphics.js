Graphics = {};


Graphics.landscapePictures = {
	"forest" : "url('css/images/forest.jpg')",
	"swamp" : "url('css/images/swamp.jpg')",
	"sea" : "url('css/images/sea.jpg')",
	"hill" : "url('css/images/hill.jpg')",
	"mountain" : "url('css/images/mountain.jpg')",
	"farmland" : "url('css/images/farmland.jpg')",
	"magic" : "url('css/images/magic.jpg')",
	"cavern" : "url('css/images/cavern.jpg')",
	"mine" : "url('css/images/mine.jpg')",
	"natives" : "url('css/images/races/elves small.jpg')"
};


Graphics.gameField = {
	width : 630,
	height : 620,
	mapWidth : 630,
	mapHeight : 515
};

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
	if (!badgeType) return;
	var place = reg || Graphics.freeTokens,
		coords = badgeType.race ? place.raceCoords : place.powerCoords,
		previousBadge = badgeType.race ? place.ui.race : place.ui.power,
		pic = badgeType.getPic(reg && reg.inDecline),
		badge;
	if (Graphics.cnt >= 2 && previousBadge && previousBadge.pic == pic && previousBadge.num.n == num) 
		return previousBadge;
	if(previousBadge)
	{
		previousBadge.remove();
		delete previousBadge;
	}
	if (!num) return;
	badge = Graphics.paper.rect(coords[0], coords[1], 50, 50)
				.attr({fill : "url(" + pic +")"}).toFront();
	badge.num = Graphics.paper.text(coords[0] + 36, coords[1] + 14, num)
		.attr({"font": '100 14px "Helvetica Neue", Helvetica', "fill" : "red",
			"text-anchor": "start"}).toFront();
	badge.num.n = num;
	badge.pic = pic;
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

Graphics.getRegBoundsColor = function(region){
	return region.ownerId ? Graphics.colors[region.ownerId] : "black";
};

Graphics.getRegColorAndOpacity = function(reg){
	var conq = canBeginConquer() && canConquer(reg), 
		def =  canBeginDefend() && canDefend(reg),
		color = conq ? 'yellow' : def ? 'blue' : 'white';
	return [color, conq || def ? 0.6 : 0];

};

Graphics.drawRegionBadges = function(region){
	var tBadge = region.getTokenBadge();
	Graphics.drawTokenBadge(region, tBadge ? tBadge.getRace() : getBaseRace(), 
			region.tokensNum);
	tBadge && Graphics.drawTokenBadge(region, tBadge.getPower(), 
				0 + region[tBadge.getPower().regPropName]);
};


Graphics.drawFreeBadges = function(){
	Graphics.freeTokens.ui.race = Graphics.drawTokenBadge(null, user().race(), user().freeTokens);
	Graphics.freeTokens.ui.power = Graphics.drawTokenBadge(null, user().specPower(), user().freePowerTokens);
};	

Graphics.update = function(map){
	if (Graphics.forbidUpdate()) return;
	var regions = map.sortedRegions(), cur, i,
		attrs;
	
	for (i = 0; i < regions.length; ++i){
		cur = regions[i];
		cur.ui.animate({"stroke" : Graphics.getRegBoundsColor(cur)}, 1000);
		attrs = Graphics.getRegColorAndOpacity(cur);
		cur.ui.animate({fill : attrs[0], 'fill-opacity' : attrs[1]}, 1000);
		Graphics.drawRegionBadges(cur);
	}
	Graphics.drawFreeBadges();
	Graphics.cnt++;
};

Graphics.assignColors = function(){
	if (Graphics.colors.length) return;
	var i;
	for (i = 0; i < game().players.length; i++) 
		Graphics.colors[game().players[i].id] = Raphael.getColor();
};


Graphics.drawMap = function(map) {
	Graphics.paper = Raphael("map", Graphics.gameField.height, Graphics.gameField.height);
	Graphics.cnt = 0;
	var paper = Graphics.paper,
		regions = map.sortedRegions(),
		selectRegion = function(reg, sel){
			return function(){
				var attrs = Graphics.getRegColorAndOpacity(reg.model),
					color = sel? 'red' : attrs[0],
					opacity = sel ? 0.7 : attrs[1];
				reg.animate({'fill-opacity': opacity, fill : color}, 300);
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
			var landscape = Graphics.getRegLandscape(region),
				strokeStyle = Graphics.getRegBoundsColor(region),
				r0 = paper.path(getSvgPath(region.coords))
					.attr({fill: landscape})
				r =	paper.path(getSvgPath(region.coords))
					.attr({	stroke : strokeStyle, "stroke-width": 3, 
					"stroke-linecap": "round"}),
					attrs = Graphics.getRegColorAndOpacity(region);
			region.ui = r;
			r.model = region;
			Graphics.drawRegionBadges(region);
			r.animate({fill : attrs[0], 'fill-opacity' : attrs[1]}, 1000);
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
	for (var i = 0; i < regions.length; ++i)
		drawRegion(regions[i]);
	var frame = paper.rect(0, 515, 630, 105).attr({fill: "LightYellow", stroke: "black"});
	Graphics.drawFreeBadges();

};

Graphics.getRegLandscape = function(region){
	return Graphics.landscapePictures[region.landscape];
};

Graphics.makePreview = function(map, div, width, height){
	var paper = Raphael(div, width, height),
		drawRegionThmb = function(region){
			var fillStyle = Graphics.getRegLandscape(region),
				r = paper.path(getSvgPath(region.coords))
					.attr({fill: fillStyle, stroke : "black",
						"stroke-width": 3, "stroke-linecap": "round"});
		}, i;
	for (i = 0; i < map.regions.length; ++i)
		drawRegionThmb(map.regions[i]);
	return paper;
};
	
	
