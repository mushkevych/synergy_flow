function render_flow_header(element, mx_flow, process_name) {
    var uow_button = $('<button class="action_button"><i class="fa fa-file-code-o"></i>&nbsp;Uow</button>').click(function (e) {
        var params = {action: 'action/get_uow', timeperiod: mx_flow.timeperiod, process_name: process_name};
        var viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=450,height=400,screenX=400,screenY=200,scrollbars=1');
    });
    var event_log_button = $('<button class="action_button"><i class="fa fa-th-list"></i>&nbsp;Event&nbsp;Log</button>').click(function (e) {
        var params = {action: 'action/get_event_log', timeperiod: mx_flow.timeperiod, process_name: process_name};
        var viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
    });
    var recover_button = $('<button class="action_button"><i class="fa fa-share-square-o"></i>&nbsp;Recover</button>').click(function (e) {
        process_job('flow/action/recover', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, null);
    });
    var reprocess_button = $('<button class="action_button"><i class="fa fa-repeat"></i>&nbsp;Reprocess</button>').click(function (e) {
        process_job('action/reprocess', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, null);
    });
    var uow_log_button = $('<button class="action_button"><i class="fa fa-file-text-o"></i>&nbsp;Uow&nbsp;Log</button>').click(function (e) {
        var params = {action: 'action/get_uow_log', timeperiod: mx_flow.timeperiod, process_name: process_name};
        var viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
    });
    var flow_log_button = $('<button class="action_button"><i class="fa fa-file-text-o"></i>&nbsp;Flow&nbsp;Log</button>').click(function (e) {
        var params = {action: 'flow/action/get_flow_log', timeperiod: mx_flow.timeperiod, process_name: process_name, flow_name: mx_flow.flow_name};
        var viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
    });

    var container = $('<div class="step_container"></div>');

    container.append($('<div class="step_section right_margin"></div>').append('<ul class="fa-ul">'
        + '<li title="Process Name"><i class="fa-li fa fa-terminal"></i>' + process_name + '</li>'
        + '<li title="Workflow Name"><i class="fa-li fa fa-random"></i>' + mx_flow.flow_name + '</li>'
        + '<li title="Timeperiod"><i class="fa-li fa fa-clock-o"></i>' + mx_flow.timeperiod + '</li>'
        + '<li title="State"><i class="fa-li fa fa-flag-o"></i>' + mx_flow.state + '</li>'
        + '</ul>'));
    container.append($('<div class="step_section"></div>')
        .append($('<div></div>').append(uow_log_button))
        .append($('<div></div>').append(flow_log_button))
        .append($('<div></div>').append(event_log_button)));
    container.append($('<div class="step_section"></div>')
        .append($('<div></div>').append(uow_button))
        .append($('<div></div>').append(recover_button))
        .append($('<div></div>').append(reprocess_button)));

    element.append(container);
    element.append('<div class="clear"></div>');
}


function render_flow_graph(steps, element) {

    // Set up zoom support
    var svg = d3.select('svg'),
        inner = svg.select('g'),
        zoom = d3.behavior.zoom().on('zoom', function () {
            inner.attr('transform', 'translate(' + d3.event.translate + ")" +
                'scale(' + d3.event.scale + ')');
        });

    svg.call(zoom);
    var render = new dagreD3.render();

    // Left-to-right layout
    var g = new dagreD3.graphlib.Graph();

    g.setGraph({
        nodesep: 70,
        ranksep: 50,
        rankdir: 'LR',
        marginx: 20,
        marginy: 20
    });

    function draw(isUpdate) {
        var step_index = 0;
        for (var step_name in steps) {
            var step = steps[step_name];

            var css_pre_completed = step.is_pre_completed ? "action_complete" : "action_pending";
            var css_main_completed = step.is_main_completed ? "action_complete" : "action_pending";
            var css_post_completed = step.is_post_completed ? "action_complete" : "action_pending";

            var html = '<div id=step_' + step_index + ' class="step_container">';
            html += '<div id=step_' + step_index + '_action_status class="step_section width_30pct">';
            html += '<span class="pre_actions action_status ' + css_pre_completed + '"></span>';
            html += '<span class="action_status ' + css_main_completed + '"></span>';
            html += '<span class="action_status ' + css_post_completed + '"></span>';
            html += '</div>';
            html += '<div class="step_section width_70pct">';
            html += '<div id=step_' + step_index + '_title class="step_detail"></div>';
            html += '<div id=step_' + step_index + '_duration class="step_detail"></div>';
            html += '<div id=step_' + step_index + '_action_buttons class="step_detail"></div>';
            html += '</div>';
            html += '</div>';
            step_index += 1;

            g.setNode(step_name, {
                labelType: 'html',
                label: html,
                rx: 5,
                ry: 5,
                padding: 0,
                class: step.state
            });

            if (step.previous_nodes) {
                if (step.previous_nodes instanceof Array) {
                    var arrayLength = step.previous_nodes.length;
                    for (var i = 0; i < arrayLength; i++) {
                        g.setEdge(step.previous_nodes[i], step_name, {
                            label: step.step_name + '/s',
                            width: 40
                        });
                    }
                } else {
                    g.setEdge(step.previous_nodes, step_name, {
                        label: step.step_name + '/s',
                        width: 40
                    });
                }
            }
        }

        // renderer draws the final graph
        inner.call(render, g);

        // now that the graph nodes are rendered, add:
        // - step name
        // - step duration
        // - action buttons
        step_index = 0;
        for (step_name in steps) {
            var step_log = $('<button class="action_mini_button" title="Get step log"><i class="fa fa-file-code-o"></i></button>').click(function (e) {
                process_job('flow/action/get_step_log', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, step_name);
            });
            var run_one = $('<button class="action_mini_button" title="Rerun this step only"><i class="fa fa-play-circle-o"></i></button>').click(function (e) {
                process_job('flow/action/run_one_step', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, step_name);
            });
            var run_from = $('<button class="action_mini_button" title="Rerun flow from this step"><i class="fa fa-forward"></i></button>').click(function (e) {
                process_job('flow/action/run_from_step', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, step_name);
            });
            var details = $('<button class="action_mini_button" title="Step details"><i class="fa fa-ellipsis-h"></i></button>').click(function (e) {
                alert('details form TBD');
            });

            $('#step_' + step_index + '_title').append('<span class=text>' + step_name + '</span>');
            if (step_name != 'start' && step_name != 'finish') {
                $('#step_' + step_index + '_duration').append('<span class=text>' + 1000 + '</span>');
                $('#step_' + step_index + '_action_buttons').append(step_log).append(run_one).append(run_from).append(details);
            }
            step_index += 1;
        }

        // Zoom and scale to fit
        var graphWidth = g.graph().width + 240;
        var graphHeight = g.graph().height + 160;
        var width = parseInt(svg.style('width').replace(/px/, ''));
        var height = parseInt(svg.style('height').replace(/px/, ''));
        var zoomScale = Math.min(width / graphWidth, height / graphHeight);
        var translate = [(width / 2) - ((graphWidth * zoomScale) / 2), (height / 2) - ((graphHeight * zoomScale) / 2)];
        zoom.translate(translate);
        zoom.scale(zoomScale);
        zoom.event(isUpdate ? svg.transition().duration(500) : d3.select('svg'));
    }

    draw();
}
