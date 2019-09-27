d3.csv("nodes.csv", function(mynodes) {

  var width = 960,
      height = 500,
      wmax = width-20,
      hmax = height-20,
      radius = 3;

  var svg = d3.select("body").append("svg")
      .attr("width", width)
      .attr("height", height);

  d3.csv('edges.csv', function(myedges) {

    myedges.forEach(function(d) {
      d.x1 = +d.x1;
      d.x2 = +d.x2;
      d.y1 = +d.y1;
      d.y2 = +d.y2;
      d.width = +d.width;
    });

    var lines = svg.append("g")
       .attr("class", "mylines")
        .selectAll(".lines")
      .data(myedges)
      .enter().append("line")
       .attr("x1", function (d) { return wmax/2 + d.x1*wmax/2; })
       .attr("x2", function (d) { return wmax/2 + d.x2*wmax/2; })
       .attr("y1", function (d) { return hmax/2 + d.y1*hmax/2; })
       .attr("y2", function (d) { return hmax/2 + d.y2*hmax/2; })
       .attr('stroke-width', function(d) { return d.width; })

  });

  mynodes.forEach(function(d) {
    d.x = +d.x;
    d.y = +d.y
    d.strength = +d.strength;
  });

   function color(mynodes) { return mynodes.strength; }
   var crange = d3.extent(mynodes, function(d) {return +d.strength;});
   var colorScale = d3.scaleSequential(d3.interpolatePlasma).domain([crange[0], crange[1]]);
   // Plasma, Inferno, Magma, Viridis, YlOrRd

   var dot = svg.append("g")
   		.attr("class", "dots")
       .selectAll(".dot")
   		.data(mynodes)
       .enter().append("circle")
   		.attr("class", "dot")
      .attr("r", radius)
      .attr("cx", function (d) { return wmax/2 + d.x*wmax/2; })
      .attr("cy", function (d) { return hmax/2 + d.y*hmax/2; })
      .style("fill", function(d) { return colorScale(color(d)); })
});
