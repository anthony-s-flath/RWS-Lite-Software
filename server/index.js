var graph_type = document.getElementById("graph-type");
var graph = document.getElementsByClassName("graph");
graph_type.addEventListener("change", (event) => {
    graph.src = `/graph?file=idk&type=${event.target.value}`;
})
