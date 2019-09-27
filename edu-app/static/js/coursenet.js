var width = 1200,
    height = 800,
    wmax = width-20,
    hmax = height-20,
    radius = 3;

var svg = d3.select("#main-svg")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

var svgback = svg.append("g");
var svgfront = svg.append("g");


d3.csv('../../static/edges_orig.csv', function(myedges) {

  myedges.forEach(function(d) {
    d.x1 = +d.x1;
    d.x2 = +d.x2;
    d.y1 = +d.y1;
    d.y2 = +d.y2;
    d.width = +d.width;
  });

  var lines = svgback.append("g")
     .attr("class", "mylines")
      .selectAll(".lines")
    .data(myedges)
    .enter().append("line")
     .attr("x1", function (d) { return wmax/2 + d.x1*wmax/2 + 10; })
     .attr("x2", function (d) { return wmax/2 + d.x2*wmax/2 + 10; })
     .attr("y1", function (d) { return hmax/2 + d.y1*hmax/2 + 10; })
     .attr("y2", function (d) { return hmax/2 + d.y2*hmax/2 + 10; })
     .style("stroke", function(d) { return d.color; })
     .style("stroke-width", function(d) { return d.width - .4; })
});

var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

d3.csv("../../static/nodes_orig.csv", function(mynodes) {

  mynodes.forEach(function(d) {
    d.x = +d.x;
    d.y = +d.y
    d.strength = +d.strength;
  });

   function color(mynodes) { return mynodes.strength; }
   var crange = d3.extent(mynodes, function(d) {return +d.strength;});
   var colorScale = d3.scaleSequential(d3.interpolatePlasma).domain([crange[0], crange[1]]);
   // Plasma, Inferno, Magma, Viridis, YlOrRd

   var mytooltip = d3.select('#main-svg').append("div")
       .attr("class", "tooltip")
       .style("opacity", 0);

   var mapLabel = svg.append("text")
       .attr("y", 50)
       .attr("x", 30)
       .style("font-family", "Quicksand")
       .style("font-size","16px")


   var dot = svgfront.append("g")
      .attr("class", "dots")
       .selectAll(".dot")
      .data(mynodes)
       .enter().append("circle")
      .attr("class", "dot")
      .attr("r", radius)
      .attr("cx", function (d) { return wmax/2 + d.x*wmax/2 + 10; })
      .attr("cy", function (d) { return hmax/2 + d.y*hmax/2 + 10; })
      .style("fill", function(d) { return colorScale(color(d)); })
      .on("mouseover", function(d){
        mapLabel.text(d.title)
      })
      .on("mouseout", mouseout);

  function mouseover(d) {
      mapLabel.text(d.title)
      mytooltip.transition() //mytooltip
       .duration(0)
       .style("opacity", .9)
       .text(d.title)
       //.style("left", d + "px")
       //.style("top", (d-28) + "px")
       .style("position", "absolute")
       .style("text-align", "center")
       .style("padding","3px")
       .style("font-family","Quicksand")
       .style("font-size", "12px")
       .style("background", "#eeeeee")
       .style("border", "0px")
       .style("border-radius", "8px")
       .style("pointer-events", "none");
       };

      function mouseout(d) {
        mapLabel.text("")
        mytooltip.transition()
         .duration(200)
         .style("opacity", 0);
      }
});
