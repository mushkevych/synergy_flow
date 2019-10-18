/* @author "Bohdan Mushkevych" */

function switchTab(evt, tab_id) {
    if (evt.currentTarget.className.includes(" active")) {
        // tab is currently active. avoid re-rendering it
        return;
    }

    let i;
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        // hide all elements with class="tabcontent"
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        // remove class "active" from all elements with class="tablinks"
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // show the tab, and add an "active" class to the button that opened the tab
    document.getElementById(tab_id).style.display = "block";
    evt.currentTarget.className += " active";
}


function renderEmptyResponse(element, process_name) {
    element[0].style.display = "block";
    element.append('<b>no workflow was found for process ' + process_name + '</b>');
}


function enlistTabs(element, name) {
    const tab_id = 'tab_' + name;
    const button = $('<button id="tab_button_' + name + '" class="tablinks" onclick="switchTab(event, \'' + tab_id + '\')">' + name + '</button>');
    element.append(button);
}


function enlistTabContent(element, mx_flow, process_name, entry_name, uow_type, active_run_mode) {
    const is_run_mode_nominal = ('run_mode_nominal' === active_run_mode) ? 'selected' : '';
    const is_run_mode_recovery = ('run_mode_recovery' === active_run_mode) ? 'selected' : '';
    const endpoint_type = ('type_freerun' === uow_type) ? 'freerun' : 'managed';

    const change_run_mode_form = '<form method="POST" action="/flow/run/mode/" onsubmit="xmlhttp.send(); return false;">'
        + '<input type="hidden" name="process_name" value="' + process_name + '" />'
        + '<input type="hidden" name="flow_name" value="' + mx_flow.flow_name + '" />'
        + '<input type="hidden" name="timeperiod" value="' + mx_flow.timeperiod + '" />'
        + '<input type="hidden" name="timeperiod" value="' + mx_flow.timeperiod + '" />'
        + '<select name="run_mode">'
        + '<option value="run_mode_nominal" ' + is_run_mode_nominal + '>Start from beginning</option>'
        + '<option value="run_mode_recovery" ' + is_run_mode_recovery + '>Continue from last successful step</option>'
        + '</select>'
        + '<button type="submit" class="action_button btn-icons btn-center" title="Apply">'
        + '<i class="fa fa-check"></i>'
        + '</button>'
        + '</form>';


    const run_mode_block = '<div class="header_layout">'
        + '<div class="header_layout_element ">On failure:</div>'
        + '<div class="header_layout_element ">&nbsp;</div>'
        + '<div class="header_layout_element ">' + change_run_mode_form + '</div>'
        + '</div>';

    const uow_button = $('<button class="action_button"><i class="fa fa-file-code-o"></i>&nbsp;Uow</button>').click(function (e) {
        const params = {
            action: endpoint_type + '/uow',
            timeperiod: mx_flow.timeperiod,
            process_name: process_name,
            entry_name: entry_name
        };
        const viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=450,height=400,screenX=400,screenY=200,scrollbars=1');
    });
    const event_log_button = $('<button class="action_button"><i class="fa fa-th-list"></i>&nbsp;Event&nbsp;Log</button>').click(function (e) {
        const params = {
            action: endpoint_type + '/log/event',
            timeperiod: mx_flow.timeperiod,
            process_name: process_name,
            entry_name: entry_name
        };
        const viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
    });
    const reprocess_button = $('<button class="action_button"><i class="fa fa-repeat"></i>&nbsp;Reprocess</button>').click(function (e) {
        processJob('tree/node/reprocess', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, null);
    });
    const uow_log_button = $('<button class="action_button"><i class="fa fa-file-text-o"></i>&nbsp;Uow&nbsp;Log</button>').click(function (e) {
        const params = {
            action: endpoint_type + '/log/uow',
            timeperiod: mx_flow.timeperiod,
            process_name: process_name,
            entry_name: entry_name
        };
        const viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
    });
    const flow_log_button = $('<button class="action_button"><i class="fa fa-file-text-o"></i>&nbsp;Flow&nbsp;Log</button>').click(function (e) {
        const params = {
            action: 'flow/flow/log',
            timeperiod: mx_flow.timeperiod,
            process_name: process_name,
            flow_name: mx_flow.flow_name
        };
        const viewer_url = '/viewer/object/?' + $.param(params);
        window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
    });

    const container = $('<div class="step_container"></div>');

    container.append($('<div class="step_section right_margin"></div>').append('<ul class="fa-ul">'
        + '<li title="Process Name"><i class="fa-li fa fa-terminal"></i>' + process_name + '</li>'
        + '<li title="Workflow Name"><i class="fa-li fa fa-random"></i>' + mx_flow.flow_name + '</li>'
        + '<li title="Timeperiod"><i class="fa-li fa fa-clock-o"></i>' + mx_flow.timeperiod + '</li>'
        + '<li title="State"><i class="fa-li fa fa-flag-o"></i>' + mx_flow.state + '</li>'
        + '</ul>'));

    container.append($('<div class="step_section">&nbsp;</div>'));
    container.append($('<div class="step_section"></div>')
        .append($('<div></div>').append(uow_log_button))
        .append($('<div></div>').append(flow_log_button))
        .append($('<div></div>').append(event_log_button)));
    container.append($('<div class="step_section"></div>')
        .append($('<div></div>').append(uow_button))
        .append($('<div></div>').append(reprocess_button)));

    const tab_content = $('<div id="tab_' + entry_name + '" class="tabcontent"></div>');
    tab_content.append(container);
    tab_content.append('<div class="clear"></div>');
    tab_content.append($('<div class="step_container"></div>').append(run_mode_block));

    element.append(tab_content);
}


function renderFlowGraph(steps) {

    const svg = d3.select('svg');
    const inner = svg.select('g');

    // Set up zoom support
    const zoom = d3.zoom().on('zoom', function () {
        inner.attr("transform", d3.event.transform);
    });
    svg.call(zoom);

    const render = new dagreD3.render();

    // Left-to-right layout
    const g = new dagreD3.graphlib.Graph();
    g.setGraph({
        nodesep: 70,
        ranksep: 50,
        rankdir: 'LR',
        marginx: 20,
        marginy: 20
    });

    function draw() {
        let step_index = 0;
        for (var step_name in steps) {
            var step = steps[step_name];

            var html = '<div id=step_' + step_index + ' class="step_container">';
            html += '<div id=step_' + step_index + '_action_status class="step_section width_30pct">';
            if (step_name !== 'start' && step_name !== 'finish') {
                html += '<span class="pre_actions action_status ' + step.pre_actionset.state + '"></span>';
                html += '<span class="action_status ' + step.main_actionset.state + '"></span>';
                html += '<span class="action_status ' + step.post_actionset.state + '"></span>';
            }
            html += '</div>';
            html += '<div class="step_section width_70pct">';
            html += '<div id=step_' + step_index + '_title class="step_detail width_70pct"></div>';
            html += '<div id=step_' + step_index + '_duration class="step_detail width_70pct"></div>';
            html += '<div id=step_' + step_index + '_action_buttons class="step_detail width_70pct"></div>';
            html += '</div>';
            html += '</div>';
            step_index += 1;

            // setNode(node_name, dict_value)
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
                    const arrayLength = step.previous_nodes.length;
                    for (let i = 0; i < arrayLength; i++) {
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

        // assign run-time function to render tooltip
        inner.selectAll('g.node')
            .each(function (step_name) {
                if (step_name === 'start' || step_name === 'finish') {
                    // no tooltip is desired for terminal points
                    return false;
                }

                $(this).tipsy({
                    gravity: 'w', opacity: 1, html: true,
                    title: function () {
                        const step = steps[step_name];
                        let html = '<p class="name">' + step_name + '</p>';
                        html += '<p class="description">' + formatJSON(step.pre_actionset.actions) + '</p>';
                        html += '<p class="description">' + formatJSON(step.main_actionset.actions) + '</p>';
                        html += '<p class="description">' + formatJSON(step.post_actionset.actions) + '</p>';
                        return html;
                    }
                });
            });

        // now that the graph nodes are rendered, add:
        // - step name
        // - step duration
        // - action buttons
        step_index = 0;
        for (step_name in steps) {
            const step_log = $('<button class="action_mini_button" title="Get step log"><i class="fa fa-file-code-o"></i></button>').click(function (e) {
                const params = {
                    action: 'flow/step/log',
                    timeperiod: mx_flow.timeperiod,
                    process_name: process_name,
                    flow_name: mx_flow.flow_name
                };
                const viewer_url = '/viewer/object/?' + $.param(params);
                window.open(viewer_url, 'Object Viewer', 'width=800,height=480,screenX=400,screenY=200,scrollbars=1');
            });
            const run_one = $('<button class="action_mini_button" title="Rerun this step only"><i class="fa fa-play-circle-o"></i></button>').click(function (e) {
                processJob('flow/run/one_step', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, step_name);
            });
            const run_from = $('<button class="action_mini_button" title="Rerun flow from this step"><i class="fa fa-forward"></i></button>').click(function (e) {
                processJob('flow/run/from_step', null, process_name, mx_flow.timeperiod, mx_flow.flow_name, step_name);
            });

            $('#step_' + step_index + '_title').append('<span class="text">' + step_name + '</span>');
            if (step_name !== 'start' && step_name !== 'finish') {
                $('#step_' + step_index + '_duration').append('<span class="text">' + steps[step_name].duration  + '</span>');
                $('#step_' + step_index + '_action_buttons').append(step_log).append(run_one).append(run_from);
            }
            step_index += 1;
        }
    }

    draw();
}
