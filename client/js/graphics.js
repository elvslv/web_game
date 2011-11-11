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
	return Graphics.redeploying || Graphics.dragging;
};

Graphics.freeTokenBadgeCoords = {
	'race' : [60, 550],
	'power' : [120, 550]
};

Graphics.REG_DOESNT_EXIST = -1;


Graphics.drawTokenBadge = function(reg){	//no arg means we're drawing
												//free tokens of user under the map pic
	var num = reg.tokensNum || (!reg && user().tokensInHand);
	if (!num) return;
	var tokenBadge = reg ? reg.getTokenBadge() : Graphics.REG_DOESNT_EXIST,
		pic = !tokenBadge ? getBaseRace().getPic(true) : 
				tokenBadge === Graphics.REG_DOESNT_EXIST ? 
				user().currentTokenBadge.getPic() :  
					tokenBadge.getPic()
		coords = reg ? reg.raceCoords : Graphics.freeTokenBadgeCoords.race,
		race = Graphics.paper.rect(coords[0], coords[1], 50, 50)
				.attr({fill : "url(" + pic +")"}).toFront();
	race.num = Graphics.paper.text(coords[0] + 36, coords[1] + 14, num)
		.attr({"font": '100 14px "Helvetica Neue", Helvetica', "fill" : "red",
			"text-anchor": "start"}).toFront();
	race.drag(
		function(dx, dy){
			Graphics.dragging = true;
			this.attr({x: this.ox + dx, y: this.oy + dy}); 
			this.num.attr({x: this.num.ox + dx, y: this.num.oy + dy}); 
		
		},
		function(){
			this.ox = this.attr("x");
			this.oy = this.attr("y");
			this.num.ox = this.num.attr("x");
			this.num.oy = this.num.attr("y");
			this.toFront();
			this.num.toFront();
		},
		function(){
			var offset = Graphics.offset();
			var posX = this.getBBox().x + offset.left;
			var posY = this.getBBox().y + offset.top;
			var newRegion = Graphics.paper.getElementByPoint(posX, posY);
			if (newRegion && newRegion.model && newRegion.model !== reg){
				if (!newRegion.race)
					newRegion.race = Graphics.drawTokenBadge(newRegion.model, 1, pic);
				else {
					var previousNum = parseInt(newRegion.race.num.attr("text"));
					newRegion.race.num.attr({"text" : previousNum + 1});
				}
			}
			Graphics.dragging = false;
			this.attr({x: this.ox, y: this.oy}); 
			this.num.attr({x: this.num.ox, y: this.num.oy});
		});
	if (reg) reg.ui.race = race;
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
	return region.ownerId ? Graphics.colors[region.ownerId] : "white";
};

Graphics.update = function(map){
	var cur, i;
	if (Graphics.forbidUpdate()) return;
	for (i = 0; i < map.regions.length; ++i){
		cur = map.regions[i];
		cur.ui.attr({fill : Graphics.getRegColor(cur)});
		Graphics.drawTokenBadge(cur);
	}
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
				reg.animate({stroke: sel ? "red" : "black"}, 300);
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
	//	var path = paths[region.landscape];
		var fillStyle = Graphics.getRegColor(region),
			r = paper.path(getSvgPath(region.coords))
				.attr({fill: fillStyle, "stroke-width": 3, "stroke-linecap": "round"});
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
	Graphics.drawTokenBadge(null);
	
};
	
