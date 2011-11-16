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

var defaultWidth = 634,
	defaultHeight = 515,
	defaultWidth1 = 630,
	defaultHeight1 = 640;

RaphaelGraphics = $.inherit({
	__constructor: function(map, div, width, height)
	{
		this.map = map;
		this.div = div ? $(div) : "map";
		this.width = width ? width : defaultWidth1;
		this.height = height ? height: defaultHeight1;
		this.colors = [];
		this.freeTokens = {
			raceCoords : [60 * width / defaultWidth1, 550 * height / defaultHeight1],
			powerCoords : [270 * width / defaultWidth1, 550 * height / defaultHeight1],
			ui : {}
		};
		this.paper = Raphael(this.div, this.width, this.height);
	},
	forbidUpdate: function(){
		return game().redeployStarted || game().defendStarted || this.dragging;
	},
	drawRegionThmb: function(region){
		var fillStyle = this.getRegPath(region),
		r = this.paper.path(getSvgPath(region.coords))
			.attr({fill: fillStyle, stroke : "black",
			"stroke-width": 3, "stroke-linecap": "round"});
		region.ui = r;
		r.model = region;
		this.drawRegionBadges(region);
	},
	getRegPath: function(region)
	{
		return paths[region.landscape];
	},
	drawMapThmb: function()
	{
		for (var i = 0; i < this.map.regions.length; ++i)
			this.drawRegionThmb(this.map.regions[i]);
	},
	selectRegion: function(reg, sel){
		return function(){
			reg.animate({stroke: sel ? "red" : 
				RaphaelGraphics.getRegBoundsColor(reg.model)}, 300);
			if (!this.dragging)
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
	drawRegion: function(region){
		var fillStyle = this.getRegColor(region),
		strokeStyle = RaphaelGraphics.getRegBoundsColor(region),
		r = this.paper.path(getSvgPath(region.coords))
			.attr({fill: fillStyle, stroke : strokeStyle,
			"stroke-width": 3, "stroke-linecap": "round"});
		region.ui = r;
		r.model = region;
		this.drawRegionBadges(region);
		r.hover(this.selectRegion(r, true), this.selectRegion(r, false));
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
				this.drawTokenBadge(region, badgeType, 1)
			else {
				this[field].num.n++;
				this[field].num.attr({"text" : this[field].num.n});
			}
		};
		return r;
	},
	drawTokenBadge: function(reg, badgeType, num){	
		if (!num) return;
		var pic = badgeType.getPic(reg !== null && reg.inDecline),
			place = reg || this.freeTokens,
			coords = badgeType.race ? place.raceCoords : place.powerCoords,
	//		previousBadge = badgeType.race ? place.ui.race : place.ui.power,
			badge; 

	//	console.log(previousBadge);
	//	if (previousBadge) previousBadge.remove();
		badge = this.paper.rect(coords[0], coords[1], 50, 50)
					.attr({fill : "url(" + pic +")"}).toFront();
		badge.num = this.paper.text(coords[0] + 36, coords[1] + 14, num)
			.attr({"font": '100 14px "Helvetica Neue", Helvetica', "fill" : "red",
				"text-anchor": "start"}).toFront();
		badge.num.n = num;
		badge.canDrag = (function(badgeType){
			return function(){
				return (!reg || (reg.ownerId === user().id && !reg.inDecline)) && 
					((game().defendStarted && !badgeType.power && !reg) ||
					(game().redeployStarted && badgeType.canStartRedeploy(reg)) ||
					(badgeType.name === 'DragonMaster' &&		//should change it someday
						canBeginDragonAttack() && canDragonAttack()));
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
				this.dragging = true;
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
				var offset = this.offset(),
					posX = this.getBBox().x + offset.left,
					posY = this.getBBox().y + offset.top,
					element = this.getElementByPoint(posX, posY),
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
				this.dragging = false;
			});
		if (reg){
			if (badgeType.race) reg.ui.race = badge;
			else reg.ui.power = badge;
			badge.r = reg.ui;
		}
		return badge;
	},
	offset: function(){
		var br = $.browser, left, top;
		if (br.opera || br.webkit) { 
			left = this.paper.canvas.offsetLeft;
			top = this.paper.canvas.offsetTop;
		} else{
			left = $(this.paper.canvas).offset().left;
			top = $(this.paper.canvas).offset().top;
		}
		return {
				left : left - $(document).scrollLeft(),		//check again 
				top : top - $(document).scrollTop()
		};						
	},
	getRegColor: function(region){
		return region.ownerId ? this.colors[region.ownerId] : "silver";
	},
	drawRegionBadges: function(region){
		var tBadge = game() ? region.getTokenBadge() : undefined;
		this.drawTokenBadge(region, tBadge ? tBadge.getRace() : getBaseRace(), 
				region.tokensNum);
		if (tBadge && tBadge.getPower().needRendering())
			this.drawTokenBadge(region, tBadge.getPower(), 
				0 + region[tBadge.getPower().regPropName]);
	},
	drawFreeBadges: function(){
		this.freeTokens.ui.race = this.drawTokenBadge(null, user().race(), user().freeTokens);
		this.freeTokens.ui.power = this.drawTokenBadge(null, user().specPower(), user().freePowerTokens);
	},
	update: function(map){
		if (this.forbidUpdate()) return;
		var cur, i
		for (i = 0; i < map.regions.length; ++i){
			cur = map.regions[i];
			cur.ui.animate({fill : this.getRegColor(cur)}, 1000);
			this.drawRegionBadges(cur);
		}
		this.drawFreeBadges();
	},
	assignColors: function(){
		if (this.colors.length) return;
		var i;
		for (i = 0; i < game().players.length; i++) 
			this.colors[game().players[i].id] = Raphael.getColor();
	},
	drawMap: function() {
		for (var i = 0; i < this.map.regions.length; ++i)
			this.drawRegion(this.map.regions[i]);
		var frame = this.paper.rect(0, 515, 630, 105).attr({fill: "LightYellow", stroke: "black"});
		this.drawFreeBadges();
	},
	clear: function()
	{
		this.paper.clear();
	}
},
{
	getRegBoundsColor: function(region){
		return "black";
		//canBeginConquer() && canConquer(region) ? "yellow" :  
			//canBeginDefend() && canDefend(region) ? "fuchsia" : "black";
	},
});



