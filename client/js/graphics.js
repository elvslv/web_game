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
	"natives" : "css/images/natives.jpg"
};

Graphics = {};

		
Graphics.drawMap = function(map) {
	Graphics.paper = Raphael("map", 630, 620);
	var paper = Graphics.paper;
	var drawRegion = function(region){
		var path = paths[region.landscape];
		var r = paper.path(getSvgPath(region.coordinates))
				.attr({fill: "url(" + path + ")", "stroke-width": 3, "stroke-linecap": "round"});
		if (region.bonus) {
			var bonusPath = paths[region.bonus];
			r.bonus = paper.circle(region.bonusCoords[0], region.bonusCoords[1], 12)
						.attr({fill : "url(" + bonusPath + ")"});
		}
		if (region.population) {
			var racePath = paths["natives"];
			r.race = paper.circle(region.raceCoords[0], region.raceCoords[1], 12)
						.attr({fill : "url(" + racePath + ")"});
		}
		region.ui = r;
		r.model = region;
		r.mouseover(function() {
			r.animate({stroke: "#ccc"}, 300).toFront();
			if (r.bonus) r.bonus.toFront();
			if (r.race) r.race.toFront();
		});
		r.mouseout(function() {
			r.animate({stroke: "black"}, 300).toFront();
			if (r.bonus) r.bonus.toFront();
			if (r.race) r.race.toFront();
		});
		return r;
		};
	for (var i = 0; i < map.regions.length; ++i)
		drawRegion(map.regions[i]);
	var frame = paper.rect(0, 515, 630, 105).attr({fill: "LightYellow", stroke: "black"});
	var t = paper.text(315, 540, "Units");
	t.attr({"font": '100 16px "Helvetica Neue", Helvetica', fill: "navy", "text-anchor": "middle"});
	var race = paper.circle(30, 580, 12).attr({fill : "black"});
	race.drag(
		function(dx, dy){
	//	There should be some code checking are there really enough units	
		this.attr({cx: this.ox + dx, cy: this.oy + dy}); 
		
	},
	function(){
		this.ox = this.attr("cx");
		this.oy = this.attr("cy");
		this.toFront();
	},
	function(){
		console.log(paper);
		var posX = this.getBBox().x + paper.canvas.offsetLeft - $(document).scrollLeft();
		var posY = this.getBBox().y + paper.canvas.offsetTop - $(document).scrollTop();
		var region = paper.getElementByPoint(posX, posY);
		if (region && region.model){
			reg = region.model;
			reg.ui.race = paper.circle(reg.raceCoords[0], reg.raceCoords[1], 12)
				.attr({fill : "black"});
		}
		this.attr({cx: this.ox, cy: this.oy}); 
	});
	var t2 = paper.text(290, 585, Client.currentUser.tokensInHand); 
	t2.attr({"font": '100 12px "Helvetica Neue", Helvetica', fill: "navy", "text-anchor": "start"});
	
};
	