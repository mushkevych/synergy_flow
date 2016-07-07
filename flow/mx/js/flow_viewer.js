function render_flow(steps, element) {

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
        for (var step_name in steps) {
            var step = steps[step_name];
            var className = step.consumers ? "running" : "stopped";
            if (step.count > 10000) {
                className += " warn";
            }

            var html = "<div>";
            html += "<span class=status>" + step.state + "</span>";
            html += "<span class=consumers>" + step.consumers + "</span>";
            html += "<span class=name>" + step_name + "</span>";
            html += "<span class=is_pre_completed>" + step.is_pre_completed + "</span>";
            html += "<span class=is_main_completed>" + step.is_main_completed + "</span>";
            html += "<span class=is_post_completed>" + step.is_post_completed + "</span>";
            html += "<span class=queue><span class=counter>" + step.count + "</span></span>";
            html += "</div>";

            g.setNode(step_name, {
                labelType: "html",
                label: html,
                rx: 5,
                ry: 5,
                padding: 0,
                class: className
            });

            if (step.previous_nodes) {
                if (step.previous_nodes instanceof Array) {
                    var arrayLength = step.previous_nodes.length;
                    for (var i = 0; i < arrayLength; i++) {
                        g.setEdge(step.previous_nodes[i], step_name, {
                            label: step.inputThroughput + "/s",
                            width: 40
                        });
                    }
                } else {
                    g.setEdge(step.previous_nodes, step_name, {
                        label: step.inputThroughput + "/s",
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

    /*
     * mock functions go here
     */

    draw();
}

/*  DEAD ELEPHANT

    // Do some mock queue status updates
    setInterval(function () {
        var stoppedWorker1Count = steps["step 3"].count;
        var stoppedWorker2Count = steps["etl_dim"].count;
        for (var id in steps) {
            steps[id].count = Math.ceil(Math.random() * 3);
            if (steps[id].inputThroughput) steps[id].inputThroughput = Math.ceil(Math.random() * 250);
        }
        steps["step 3"].count = stoppedWorker1Count + Math.ceil(Math.random() * 100);
        steps["etl_dim"].count = stoppedWorker2Count + Math.ceil(Math.random() * 100);
        draw(true);
    }, 1000);

    // Do a mock change of worker configuration
    setInterval(function () {
        steps["step 2"] = {
            "consumers": 0,
            "count": 0,
            "previous_nodes": "start",
            "inputThroughput": 50
        }
    }, 5000);
*/
