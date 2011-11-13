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

Graphics.forbidUpdate = function(){
	return game().redeployStarted || game().defendStarted || Graphics.dragging;
};

Graphics.freeTokenBadgeCoords = {
	race : [60, 550],
	power : [120, 550]
};

Graphics.REG_DOESNT_EXIST = -1;


Graphics.drawTokenBadge = function(reg, drop){	
	var freeTokenBadge = !reg,
		num = drop ? 1 : freeTokenBadge ? user().freeTokens : reg.tokensNum;
	if (!num) return;
	var tokenBadge = drop ? user().currentTokenBadge : 
			!freeTokenBadge ? reg.getTokenBadge() : 
				Graphics.REG_DOESNT_EXIST,	
		pic = !tokenBadge ? getBaseRace().getPic(true) : 			
				tokenBadge === Graphics.REG_DOESNT_EXIST ? 			
				user().currentTokenBadge.getPic() :  
					tokenBadge.getPic(),
		coords = freeTokenBadge ? Graphics.freeTokenBadgeCoords.race : reg.raceCoords;
		race = Graphics.paper.rect(coords[0], coords[1], 50, 50)
				.attr({fill : "url(" + pic +")"}).toFront();
	race.num = Graphics.paper.text(coords[0] + 36, coords[1] + 14, num)
		.attr({"font": '100 14px "Helvetica Neue", Helvetica', "fill" : "red",
			"text-anchor": "start"}).toFront();
	race.num.n = num;
	race.canDrag = (function(t){
		return function(){
			return (t || (reg.ownerId === user().id && !reg.inDecline)) && 
				((game().defendStarted && isDefendingPlayer() && t) ||
				(game().redeployStarted && isActivePlayer() && !t));
		};
	}(freeTokenBadge));
	race.drag(
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
					return that.tempCopy === undefined;
				},	
				restore = function(){
					that.num.attr({"text" : that.num.n});
					that.attr({x: that.ox, y: that.oy}); 
					that.num.attr({x: that.num.ox, y: that.num.oy});
				};
	//		console.log(element);
			if (element) newRegion = element.r ? element.r : element; 
			
			if (newRegion && newRegion.model && 
					newRegion.model.ownerId === user().id && 
					(freeTokenBadge || newRegion.model.id !== reg.id)){
				if (!newRegion.race) 	
					Graphics.drawTokenBadge(newRegion.model, true);
				else {
					newRegion.race.num.n++;
					newRegion.race.num.attr({"text" : newRegion.race.num.n});
				}
				if (!last()) {
					this.num.n--;
					restore();
				} else { 
					if (reg)
						reg.ui.race = undefined;
					console.log(reg.ui.race);
					console.log(this.race);
					this.num.remove();
					this.remove();
				}
				if (!game().redeployRegions[newRegion.model.id])	//not quite the place
					game().redeployRegions[newRegion.model.id] = 0;
				game().redeployRegions[newRegion.model.id]++;
				if (reg) 
					game().redeployRegions[reg.id]--;
				else
					user().freeTokens--;
					
			} else restore(); 
								
								
			if (!last()) {
				this.tempCopy.remove();
				delete this.tempCopy;
			}
			Graphics.dragging = false;
		});
	if (reg) {
		reg.ui.race = race;
		race.r = reg.ui;
	}
	return race;
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
			left : left - $(document).scrollLeft(), 
			top : top - $(document).scrollTop()
	};
};

Graphics.getRegColor = function(region){
	return region.ownerId ? Graphics.colors[region.ownerId] : "silver";
};

Graphics.getRegBoundsColor = function(region){
	return canBeginConquer() && canConquer(region) ? "yellow" :  
		canBeginDefend() && canDefend(region) ? "fuchsia" : "black";
};

Graphics.update = function(map){
	var cur, i;
	if (Graphics.forbidUpdate()) return;
	for (i = 0; i < map.regions.length; ++i){
		cur = map.regions[i];
		cur.ui.animate({fill : Graphics.getRegColor(cur)}, 1000);
		Graphics.drawTokenBadge(cur);
	}
	Graphics.freeTokensBadge = Graphics.drawTokenBadge();
};

		
Graphics.drawMap = function(map) {
	Graphics.paper = Raphael("map", 630, 620);
	var paper = Graphics.paper,
		assignColors = function(){
		var i;
		Graphics.colors = [];
		for (i = 0; i < game().players.length; i++) 
			Graphics.colors[game().players[i].id] = Raphael.getColor();
		
	},  selectRegion = function(reg, sel){
			return function(){
				reg.animate({stroke: sel ? "red" : 
					Graphics.getRegBoundsColor(reg.model)}, 300);
				if (!Graphics.dragging)
					reg.toFront();
				if (reg.race) {
					reg.race.toFront();
					if (reg.race.num) {
						reg.race.num.toFront();
					}
				}
				
			}
	},  drawRegion = function(region){
		var fillStyle = Graphics.getRegColor(region),
			strokeStyle = Graphics.getRegBoundsColor(region),
			r = paper.path(getSvgPath(region.coords))
				.attr({fill: fillStyle, stroke : strokeStyle,
				"stroke-width": 3, "stroke-linecap": "round"});
		region.ui = r;
		r.model = region;
		Graphics.drawTokenBadge(region);
		r.hover(selectRegion(r, true), selectRegion(r, false));
		r.click(Interface.getRegionInfo(region));
		return r;
	};
	assignColors();
	for (var i = 0; i < map.regions.length; ++i)
		drawRegion(map.regions[i]);
	var frame = paper.rect(0, 515, 630, 105).attr({fill: "LightYellow", stroke: "black"});
	Graphics.freeTokenBadge = Graphics.drawTokenBadge();

};
	
