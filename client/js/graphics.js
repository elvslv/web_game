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
	Graphics.paper = Raphael("map", 630, 515);
	var paper = Graphics.paper;
	console.log(paper);
	var drawRegion = function(region){
		var path = paths[region.landscape];
		var stroke = region === Client.selectedRegion ? "#ccc" : "black";
		var r = paper.path(getSvgPath(region.coordinates))
				.attr({fill: "url(" + path + ")", "stroke" : stroke, "stroke-width": 3, "stroke-linecap": "round"});
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
		r.click(function() {
		if (Client.selectedRegion)
			Client.selectedRegion.ui.animate({stroke: "black"}, 300);
			r.animate({stroke: "#ccc"}, 300);
			r.toFront();
			if (r.bonus) r.bonus.toFront();
			if (r.race) r.race.toFront();
			Client.selectedRegion = region;
		});
		return r;
		};
    for (var i = 0; i < map.regions.length; ++i)
		drawRegion(map.regions[i]);
		
};
	/*	

Graphics.drawRegion = function(region, ctx){
	var drawPolygon = function(data) {
		var i = 0; 
		ctx.beginPath(); 
		ctx.moveTo(data.coordinates[0].x, data.coordinates[0].y);
		for (i = 0; i < data.coordinates.length; ++i) 
			ctx.lineTo(data.coordinates[i].x, data.coordinates[i].y);
		ctx.closePath();
		ctx.stroke();
		ctx.fill();
		if (data === Client.currRegion) {
	 		ctx.fillStyle = 'rgba(255, 0, 255, 0.2)';
			ctx.fill();
		}
	};
	if (region.fillStyle){
		ctx.fillStyle = region.fillStyle;
		drawPolygon(region);
		ctx.fill();
		if (region.raceImg)
			ctx.drawImage(region.raceImg, region.raceCoords[0], 
				region.raceCoords[1], 30, 30);
		if (region.bonus)
			ctx.drawImage(region.bonusImg, region.bonusCoords[0], 
				region.bonusCoords[1], 30, 30);
		return;
	}
	
	var landImg = new Image();
	landImg.onload = function() {
		region.fillStyle = ctx.createPattern(landImg, 'repeat');
		ctx.fillStyle = region.fillStyle;
		drawPolygon(region);
	};
	landImg.src = paths[region.landscape];
	if (region.population) {
		region.raceImg = new Image();
		region.raceImg.onload = function(){
			ctx.drawImage(region.raceImg, region.raceCoords[0], region.raceCoords[1], 30, 30);
		};
		region.raceImg.src = paths['natives'];
	}
	if (region.bonus) {
		region.bonusImg = new Image();
		region.bonusImg.onload = function(){
			ctx.drawImage(region.bonusImg, region.bonusCoords[0], region.bonusCoords[1], 30, 30);
		};
		region.bonusImg.src = paths[region.bonus];
	};
};




function drawMap(map){
	var kin = new Kinetic("map");
	var ctx = kin.getContext();
	var canvas = kin.getCanvas();
	ctx.lineWidth = 7;
	var i = 0;
	for (i = 0; i < map.regions.length; ++i)
		Graphics.drawRegion(map.regions[i], ctx);
	canvas.addEventListener("mousedown", function(){
			console.log(window.evt);
            var mousePos = kin.getMousePos();
			console.log(mousePos);
			var region = getRegion(mousePos);
			if (region){
				Client.currRegion = region;
				Graphics.drawRegion(region);	
			}
        });
};*/