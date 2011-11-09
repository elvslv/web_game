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

Graphics.drawTokenBadge = function(reg, num, pic){
	coords = reg ? reg.raceCoords : [60, 550];
	var race = Graphics.paper.rect(coords[0], coords[1], 50, 50)
				.attr({fill : "url(" + pic +")"});
	race.num = Graphics.paper.text(coords[0] + 36, coords[1] + 7, num)
		.attr({"font": '100 14px "Helvetica Neue", Helvetica', "fill" : "red",
			"text-anchor": "start"})
		.toFront();
	race.drag(
		function(dx, dy){
	//	There should be some code checking are there really enough units	
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
		var posX = this.getBBox().x + Graphics.paper.canvas.offsetLeft - $(document).scrollLeft();
		var posY = this.getBBox().y + Graphics.paper.canvas.offsetTop - $(document).scrollTop();
		var newRegion = Graphics.paper.getElementByPoint(posX, posY);
		if (newRegion && newRegion.model && newRegion.model !== reg){
			Graphics.drawTokenBadge(newRegion.model, 1, pic);
		}
		this.attr({x: this.ox, y: this.oy}); 
		this.num.attr({x: this.num.ox, y: this.num.oy});
	});
	if (reg) reg.ui.race = race;
};

		
Graphics.drawMap = function(map) {
	Graphics.paper = Raphael("map", 630, 620);
	var paper = Graphics.paper;
	var selectRegion = function(reg, sel){
			return function(){
				reg.animate({stroke: sel ? "red" : "black"}, 300).toFront();
				if (reg.bonus) r.bonus.toFront();
				if (reg.race) {
					reg.race.toFront();
					if (reg.race.num)
						reg.race.num.toFront();
				}
			}
	};
	var drawRegion = function(region){
		var path = paths[region.landscape];
		var r = paper.path(getSvgPath(region.coords))
				.attr({fill: "url(" + path + ")", "stroke-width": 3, "stroke-linecap": "round"});
		if (region.population) {
			var racePath = paths["natives"];
			r.race = paper.circle(region.raceCoords[0], region.raceCoords[1], 12)
						.attr({fill : "url(" + racePath + ")"});
		}
		region.ui = r;
		r.model = region;
		r.mouseover(selectRegion(r, true));
		r.mouseout(selectRegion(r, false));
		r.click(Interface.getRegionInfo(region));
		return r;
	};
	for (var i = 0; i < map.regions.length; ++i)
		drawRegion(map.regions[i]);
	var frame = paper.rect(0, 515, 630, 105).attr({fill: "LightYellow", stroke: "black"});
//	if (Client.currentUser.tokenInHand)
		Graphics.drawTokenBadge(null, Client.currentUser.tokenInHand, paths.natives);
};
	