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
var testData = {
	'mapName': 'map1', 
	'playersNum': 2, 
	'turnsNum': 10,
	'regions' : 
 	[
		{	// 1
			'landDescription' : ['border', 'coast'],  
			'bonus' : 'magic',
			'landscape': 'forest',
			'coordinates' : [[0, 0], [0, 128], [46, 145], [125, 140], [103, 0]],
	 		'adjacent' : [2, 6],
			'bonusCoords' : [74, 30],
			'raceCoords': [31, 36],
			'powerCoords' : [26, 96]
	 	},
		{	// 2
	 		'landDescription' : ['border', 'coast'], 
			'bonus' : 'magic',
			'landscape': 'sea',
			'coordinates' : [[103, 0], [125, 140], [202, 103], [258, 101], [275, 77], [264, 0]],
	 		'adjacent' : [1, 3, 6, 7],
			'raceCoords': [184, 73],
			'powerCoords' : [234, 53]
	 	},
			
			
		{	// 3
	 		'landDescription' : ['coast'],  
			'bonus' : 'magic',
			'landscape': 'farmland',
			'coordinates' : [[264, 0], [275, 77], [258, 101], [273, 137], [295, 142], [391, 109], [409, 94], [393, 42], [403, 0]],
	 		'adjacent' : [2, 7, 6, 8],
			'bonusCoords' : [307, 94],
			'raceCoords': [330, 32],
			'powerCoords' : [364, 83]
	 	},
		
		{	// 4
	 		'landDescription' : ['border', 'coast'], 
			'bonus' : 'mine',
			'landscape': 'forest',
	 		'adjacent' : [3, 5, 8, 9, 10],
			'coordinates' : [[403, 0], [392, 42], [409, 94], [391, 109], [422, 176], [508, 158], [535, 104], [502, 78], [555, 0]],
			'raceCoords': [8, 412],
			'powerCoords' : [444, 39],
			'bonusCoords' : [459, 75]
	 	},

		{	//5
	 		'landDescription' : ['border'], 
			'landscape': 'swamp',	
			'bonus' : 'cavern',
			'coordinates' : [[555, 0],  [502, 78], [535, 104], [630, 120], [630, 0]],
	 		'adjacent' : [4, 10],
			'raceCoords': [560, 4],
			'powerCoords' : [570, 55],
			'bonusCoords' : [548, 68]
	 	},
			
		{	//6
	 		'landDescription' : ['border', 'coast'],
			'landscape' : 'hill',
			'coordinates' : [[0, 128], [46, 145], [125, 140], [130, 253], [89, 235], [0, 279]],		
	 		'adjacent' : [1, 2, 7, 11],
			'raceCoords': [63, 145],
			'powerCoords' : [6, 195]
	 	},

		{	//7
	 		'landDescription' : ['mountain', 'coast'],  
	 		'adjacent' : [2, 3, 6, 8, 11, 12],
			'bonus' : 'mine',
			'landscape' : 'mountain',
			'coordinates' : [[125, 140], [130, 253], [160, 251], [268, 218], [303, 172], [295, 142], [273, 137], [258, 101], [202, 103]],
			'bonusCoords': [263, 166],
			'raceCoords': [150, 190],
			'powerCoords' : [167, 35],
	 	},

		{	//8
	 		'landDescription' : [ 'coast'], 
	 		'adjacent' : [3, 4, 7, 9, 12, 13],
			'coordinates' : [[268, 218], [303, 172], [295, 142], [391, 109], [422, 176], [446, 232], [393, 273], [348, 248], [309, 251]],
			'landscape' : 'hill',
			'raceCoords': [300, 191],
			'powerCoords' : [333, 137],
	 	},

		{	//9
	 		'landDescription' : [],  
			'landscape' : 'sea',
			'coordinates' : [[393, 273], [446, 232], [422, 176], [508, 158], [547, 238], [565, 271], [508, 314]],
	 		'adjacent' : [4, 8, 10, 13, 14],
			'raceCoords': [448, 240],
			'powerCoords' : [453, 180]
 		},

		{	//10
	 		'landDescription' : ['border', 'coast'],
			'landscape' : 'mountain',
	 		'adjacent' : [4, 5, 9, 14],
			'coordinates' : [[508, 158],  [535, 104], [630, 120], [630, 240], [547, 238]],
			'raceCoords': [546, 180],
			'powerCoords' : [536, 123]
	 	},

		{	//11
	 		'landDescription' : ['border'],  
			'landscape' : 'sea',
	 		'adjacent' : [6, 7, 12, 15],
			'coordinates' : [[0, 279],[89, 235],[130, 253], [160, 251], [155, 340], [113, 343], [0, 375]],
			'raceCoords': [7, 305],
			'powerCoords' : [65, 253]
	 	},

		{	//12
	 		'landDescription' : ['coast', 'farmland'], 
			'landscape' : 'farmland',
			'coordinates' : [[160, 251], [155, 340], [216, 339], [278, 329], [310, 287], [309, 251], [268, 218]],
	 		'adjacent' : [7, 8, 11, 13, 15, 17],
			'raceCoords': [214, 253],
			'powerCoords' : [163, 287]
	 	},

		{	//13
	 		'landDescription' : ['coast'],  
			'coordinates' : [[278, 329], [310, 287], [309, 251], [348, 248], [393, 273],  [508, 314], [512, 371], [405, 410]],
			'landscape' : 'forest',
	 		'adjacent' : [8, 9, 12, 14, 17, 18, 19],
			'raceCoords': [380, 313],
			'powerCoords' : [318, 215]
	 	},

		{	//14
	 		'landDescription' : ['border', 'coast'],  
			'bonus' : 'magic',
			'coordinates' : [[508, 314], [512, 371], [556, 415], [630, 416], [630, 240], [547, 238], [565, 271]], 
			'landscape' : 'farmland',
	 		'adjacent' : [9, 10, 13, 19, 20],
			'bonusCoords' : [599, 275],
			'raceCoords': [546, 348],
			'powerCoords' : [565, 287]
		
	 	},

		{	//15
	 		'landDescription' : ['border', 'coast'], 
	 		'adjacent' : [11, 12, 16, 17],
			'coordinates' : [[0, 375], [113, 343], [155, 340],[216, 339],[245, 385], [184, 465], [0, 421]],
			'bonus' : 'magic',
			'bonusCoords' : [192, 379],
			'landscape' : 'swamp',
			'raceCoords': [87, 375],
			'powerCoords' : [28, 376] 
		},

		{	//16
	 		'landDescription' : ['border'],
			'landscape' : 'hill',
			'coordinates' : [[0, 421], [184, 465], [186, 515], [0, 515]],
			'bonus' : 'cavern',
			'bonusCoords' : [129, 483],
			'raceCoords': [62, 458],
			'powerCoords' : [6, 458],
	 		'adjacent' : [15, 17]
	 	},

		{	//17
	 		'landDescription' : ['border'],  
			'landscape' : 'mountain',
			'bonus' : 'mine',
	 		'adjacent' : [12, 13, 15, 16, 18],
			'coordinates' : [[216, 339], [278, 329], [335, 365], [289, 515], [186, 515], [184, 465], [245, 385]],
			'bonusCoords' : [273, 360],
			'raceCoords': [202, 460],
			'powerCoords' : [244, 398]
	 	},

		{	//18
	 		'landDescription' : ['border'],  
			'coordinates' : [[289, 515], [335, 365], [405, 410], [408, 515]],
			'bonus' : 'cavern',
			'landscape' : 'hill',
			'bonusCoords' : [378, 486],
	 		'adjacent' : [13, 17, 19],
			'raceCoords': [324, 411],
			'powerCoords' : [308, 464]
	 	},

		{	//19
	 		'landDescription' : ['border', 'swamp', 'mine'], 
			'coordinates' : [[408, 515], [405, 410], [512, 371], [556, 415], [518, 468], [523, 515]],
			'bonus' : 'mine',
			'landscape' : 'swamp',
	 		'adjacent' : [13, 14, 18, 20],
			'bonusCoords' : [514, 418],
			'raceCoords': [419, 411],
			'powerCoords' : [437, 466]
	 	},

		{	//20
	 		'landDescription' : ['border'], 
			'coordinates' : [[523, 515], [518, 468], [556, 415], [630, 416], [630, 515]],
	 		'landscape' : 'mountain',
			'adjacent' : [14, 19],
			'raceCoords': [529, 466],
			'powerCoords' : [582, 422]
		}
			
			
	  ]
};

function drawMap(map){
		
	globalCompositeOperation = 'darker';

	var canvas = document.getElementById("map");
	if (canvas.getContext){
	    var ctx = canvas.getContext('2d'), i = 0;
		ctx.lineWidth = 7;
		var drawPolygon = function(data) {
			var i = 0; 
			ctx.beginPath(); 
			ctx.moveTo(data.coordinates[0][0], data.coordinates[0][1]);
			for (i = 0; i < data.coordinates.length; ++i) 
		    	ctx.lineTo(data.coordinates[i][0], data.coordinates[i][1]);
			ctx.closePath();
			ctx.stroke();
			ctx.fill();
		};
		var drawRegion = function(region){
			var landImg = new Image();
			landImg.onload = function() {
				ctx.fillStyle = ctx.createPattern(landImg, 'repeat');
				drawPolygon(region);
			};
			landImg.src = paths[region.landscape];
			if (region.population) {
				var raceImg = new Image();
				raceImg.onload = function(){
					ctx.drawImage(bonusImg, region.raceCoords[0], region.raceCoords[1], 30, 30);
				};
				raceImg.src = paths['natives'];
			}
			if (region.bonus) {
				var bonusImg = new Image()
				bonusImg.onload = function(){
					ctx.drawImage(bonusImg, region.bonusCoords[0], region.bonusCoords[1], 30, 30);
				};
				bonusImg.src = paths[region.bonus];
			};
		};
		for (i = 0; i < map.regions.length; ++i)
			drawRegion(map.regions[i]);
	}
				
}