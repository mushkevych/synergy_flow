function render_flow(data, element) {

    var workers = data;

    // Set up zoom support
    var svg = d3.select("svg"),
        inner = svg.select("g"),
        zoom = d3.behavior.zoom().on("zoom", function () {
            inner.attr("transform", "translate(" + d3.event.translate + ")" +
                "scale(" + d3.event.scale + ")");
        });

    svg.call(zoom);
    var render = new dagreD3.render();

    // Left-to-right layout
    var g = new dagreD3.graphlib.Graph();

    g.setGraph({
        nodesep: 70,
        ranksep: 50,
        rankdir: "LR",
        marginx: 20,
        marginy: 20
    });

    function draw(isUpdate) {
        for (var id in workers) {
            var worker = workers[id];
            var className = worker.consumers ? "running" : "stopped";
            if (worker.count > 10000) {
                className += " warn";
            }
            var html = "<div>";
            html += "<span class=status></span>";
            html += "<span class=consumers>" + worker.consumers + "</span>";
            html += "<span class=name>" + id + "</span>";
            html += "<span class=queue><span class=counter>" + worker.count + "</span></span>";
            html += "</div>";

            g.setNode(id, {
                labelType: "html",
                label: html,
                rx: 5,
                ry: 5,
                padding: 0,
                class: className
            });

            if (worker.previous_nodes) {
                if (worker.previous_nodes instanceof Array) {
                    var arrayLength = worker.previous_nodes.length;
                    for (var i = 0; i < arrayLength; i++) {
                        g.setEdge(worker.previous_nodes[i], id, {
                            label: worker.inputThroughput + "/s",
                            width: 40
                        });
                    }
                } else {
                    g.setEdge(worker.previous_nodes, id, {
                        label: worker.inputThroughput + "/s",
                        width: 40
                    });
                }
            }
        }

        inner.call(render, g);

        // Zoom and scale to fit
        var graphWidth = g.graph().width + 80;
        var graphHeight = g.graph().height + 40;
        var width = parseInt(svg.style("width").replace(/px/, ""));
        var height = parseInt(svg.style("height").replace(/px/, ""));
        var zoomScale = Math.min(width / graphWidth, height / graphHeight);
        var translate = [(width / 2) - ((graphWidth * zoomScale) / 2), (height / 2) - ((graphHeight * zoomScale) / 2)];
        zoom.translate(translate);
        zoom.scale(zoomScale);
        zoom.event(isUpdate ? svg.transition().duration(500) : d3.select("svg"));
    }

    // Do some mock queue status updates
    setInterval(function () {
        var stoppedWorker1Count = workers["step 3"].count;
        var stoppedWorker2Count = workers["etl_dim"].count;
        for (var id in workers) {
            workers[id].count = Math.ceil(Math.random() * 3);
            if (workers[id].inputThroughput) workers[id].inputThroughput = Math.ceil(Math.random() * 250);
        }
        workers["step 3"].count = stoppedWorker1Count + Math.ceil(Math.random() * 100);
        workers["etl_dim"].count = stoppedWorker2Count + Math.ceil(Math.random() * 100);
        draw(true);
    }, 1000);

    // Do a mock change of worker configuration
    setInterval(function () {
        workers["step 2"] = {
            "consumers": 0,
            "count": 0,
            "previous_nodes": "start",
            "inputThroughput": 50
        }
    }, 5000);

    draw();
}