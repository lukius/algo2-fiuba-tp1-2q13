var war = {
    run : function() {
        this.read_json_and_execute('config', this.parse_config_and_run);
    },

    exploding : false,

    parse_config_and_run : function(config_data) {
        war.config = {
            n : config_data.n,
            m : config_data.m,
            max_energy : config_data.e,
            gx : config_data.gx,
            gy : config_data.gy,    
            t : config_data.t,
            iteration_filename : config_data.iteration_filename,
            action_filename : config_data.action_filename,
            army1_name : config_data.army1_name,
            army2_name : config_data.army2_name,
            width : 700,
            height : 700,
            separation : 1.8,
            max_radius : 10,
            min_radius : 5,
            current_iteration : 1,
            button_width : 50,
            cell_width : 25,
            cell_height : 25,
            cell_color : d3.rgb(200,200,200).brighter(0.3),
            army1_color : d3.rgb(200,60,60).brighter(0.5),
            army2_color : d3.rgb(60,60,100).brighter(0.5),
            army1_range_color : d3.rgb(200,100,100).brighter(2),
            army2_range_color : d3.rgb(60,60,100).brighter(3)
        }
        war.do_run();
    },

    do_run : function() {
        var ground = d3.select('#ground');
        var svg = ground.append('svg')
                            .attr('width', this.config.width)
                            .attr('height', this.config.height);
        this.svg = svg;
        this.set_slider();
        this.set_key_press_callbacks();
        this.create_territory();
        this.draw_armies_tables();
        this.render_soldiers_from(this.config.current_iteration);
    },

    set_slider : function() {    
        var slider = d3.slider()
                        .axis(false)
                        .min(1)
                        .max(war.config.t)
                        .step(1)
                        .on("slide", function(event, value) {
		                        var iteration = war.config.current_iteration;
		                        war.svg.selectAll('.grenade').remove();
		                        war.clear_winner();
		                        if(war.exploding)
		                            d3.selectAll('.cell').transition().duration(750).attr('fill', war.config.cell_color);
		                        war.config.current_iteration = value;
		                        if(value == iteration + 1)
		                            war.go_to_iteration(value);
		                        else
		                            war.render_soldiers_from(value);
                        });
        
        var slider_div_width = (war.config.cell_width + war.config.separation)*war.config.m -
        						war.config.separation - war.config.button_width - 30;
        var slider_div = d3.select('#slide')
                            .attr('style', 'width:' + slider_div_width.toString())
                            .call(slider);
        war.slider = slider;
        d3.select("#button")
        	.on("click", function() {
        		if(war.can_slide_forward())
        			war.move_slider(war.config.current_iteration + 1);
        	});
    },

    move_slider : function(value) {
    	war.clear_cells();
        war.slider.slide_to(value);
    },

    can_slide_forward : function() {
        return war.config.current_iteration < war.config.t;
    },

    can_slide_backwards : function() {
        return war.config.current_iteration > 1;
    },

    set_key_press_callbacks : function() {
        d3.select("body")
            .on("keydown", function() {
                function is_left_arrow(key_code) {
                    return key_code == 37;
                }
                function is_right_arrow(key_code) {
                    return key_code == 39;
                }
                function is_spacebar(key_code) {
                    return key_code == 32;
                }
        
                var key_code = d3.event.keyCode;
                if(war.can_slide_forward() && 
                    (is_right_arrow(key_code) || is_spacebar(key_code)))
                    war.move_slider(war.config.current_iteration + 1);
                else if(war.can_slide_backwards() && is_left_arrow(key_code))
                    war.move_slider(war.config.current_iteration - 1);
            });
    },
    
    clear_cells : function() {
        d3.selectAll('.cell').attr('fill', war.config.cell_color);    	
    },

    read_json_and_execute : function(json_filename, callback) {
        var encoded_file_url = encodeURIComponent(json_filename);
        d3.json(encoded_file_url, callback);    
    },

    render_soldiers_from : function(iteration_number) {
        this.read_json_and_execute(this.config.iteration_filename + iteration_number, war.render_soldiers);
    },

    go_to_iteration : function(iteration_number) {
        this.read_json_and_execute(this.config.action_filename + (iteration_number - 1),
                                   function (data) {
                                        war.render_actions_and_soldiers(data, iteration_number)
                                   });
    },

    create_territory : function() {
        var territory = [];
        for (var k = 0; k < this.config.n; k += 1) {
	        var row = [];
	        d3.range(this.config.m).forEach(function(i) { row.push([k,i]) } );
            territory.push(row);
        }
        
        var grp = this.svg.selectAll('g')
                            .data(territory)
                            .enter()
                            .append('g')
                            .attr('transform', function(d, i) {
                                return 'translate(0, ' + (war.config.cell_height + war.config.separation) * i + ')';
                            });
        
        var rect = grp.selectAll('.cell')
	                    .data(function(d) { return d; })
	                    .enter()
	                    .append('rect')
                            .attr('class', 'cell')
		                    .attr('x', function(d, i) { return (war.config.cell_width + war.config.separation) * i; })
		                    .attr('width', this.config.cell_width)
		                    .attr('height', this.config.cell_height)
                            .attr('id', function(d, i) { return 'r' + d[0] + '_' + d[1]; })
		                    .attr('fill', this.config.cell_color);
    },

    render_soldiers : function(soldier_data) {
        var soldiers = war.svg.selectAll('.soldier').data(soldier_data, function(d) { return d.name; });
                                
        soldiers.enter()
                    .append('circle')
                    .attr("fill", function(d, i) { return d.army == 1 ? war.config.army1_color : war.config.army2_color; })
                    .attr("class", "soldier")
                    .on("mouseover", function(d, i) {
                        var range_color = d.army == 1 ? war.config.army1_range_color : war.config.army2_range_color;
                        war.switch_color(d, range_color);
                     })
                    .on("mouseout", function(d, i) { war.switch_color(d, war.config.cell_color); });
        
        soldiers.transition()
                    .duration(750)
                    .attr("cx", function(d, i) { return war.config.cell_width/2 + (war.config.cell_width + war.config.separation) * d.col; })
                    .attr("cy", function(d, i) { return war.config.cell_height/2 + (war.config.cell_height + war.config.separation) * d.row; })
                    .attr("r", function(d, i) {
                        if(d.e == 0)
                            return 0;
                        var weight = d.e / war.config.max_energy;
                        return (1-weight)*war.config.min_radius + weight*war.config.max_radius; 
                    });
    
        
        war.set_tooltip();
        war.update_armies_tables(soldier_data);
        war.notify_winner_if_game_ended();
    },

    set_tooltip : function() {
        $('svg .soldier').tipsy({ 
            gravity: 'w', 
            html: true, 
            title: function() {
              var data = this.__data__;
              return "<b>" + data.name + "</b> - energy: <b>" + data.e + "</b>"; 
            }
        });
    },

    notify_winner_if_game_ended : function() {
        function do_banner_transition(selection, delay) {
            if(typeof delay == "undefined")
                delay = 2000;
            selection.transition()
                    .delay(delay)
                    .duration(500) 
                    .attr('style','color:yellow')
                    .transition()
                    .duration(500)
                    .attr('style','color:white')
                    .each("end", function() { do_banner_transition(selection, 0); });
        }

        function do_soldier_transition(selection, delay) {
            if(typeof delay == "undefined")
                delay = 2000;
            selection.transition()
                    .delay(delay)
                    .duration(400) 
                    .attr('r', function(d, i) { return Math.random() * 20; })
                    .transition()
                    .duration(500)
                    .attr('r', function(d, i) { return Math.random() * 20; })
                    .each("end", function() { do_soldier_transition(selection, 0); });
        }

        function notify_winner(army_id, name) {
            d3.select('#winner')
                .append('p')
                .attr('style','align:center')
                .text('gana ' + name + '!')
                .call(do_banner_transition);

            d3.selectAll('.soldier')
                .filter(function (d) { return d.army == army_id; })
                    .call(do_soldier_transition);
        }

        if(war.config.current_iteration == war.config.t) {
            var army1_points = 0,
                army2_points = 0;
            d3.selectAll('.soldier').each(function (d) {
                if(d.army == 1)
                    army2_points += war.config.max_energy - d.e;
                else if(d.army == 2)
                    army1_points += war.config.max_energy - d.e;
            });
            if(army1_points > army2_points)
                notify_winner(1, war.config.army1_name);
            else if(army2_points > army1_points)
                notify_winner(2, war.config.army2_name);
        }
    },

    clear_winner : function() {
        d3.select('#winner').selectAll('p').remove();
    },

    draw_armies_tables : function() {
        war.draw_army_table(1);
        war.draw_army_table(2);
    },

    update_armies_tables : function(soldier_data) {
        war.update_army_table(1, soldier_data.filter(function (d) { return d.army == 1; }));
        war.update_army_table(2, soldier_data.filter(function (d) { return d.army == 2; }));
    },

    update_army_table : function(army_id, soldier_data) {
        var table_container = d3.select('#army' + army_id);
        var table = table_container.select('table');
        var data = table.selectAll('.army_table_data').data([army_id]);
        var color = army_id == 1 ? war.config.army1_range_color : war.config.army2_range_color;
        data.enter()
                .append('table')
                .attr('class', 'army_table_data');

        var soldier_row = data.selectAll('.army_table_data_row').data(soldier_data, function (d) { return d.name; }); 
        soldier_row.enter().append('tr').attr('class', 'army_table_data_row');
        var x = soldier_row.selectAll('.soldier_name').data(function (d) { return [d]; }); 
        x.enter()
               .append('td')
                .append('p')
                 .attr('class', 'soldier_name')
                .text(function (d,i) { return d.name; })
                .on('mouseover', function(d, i) { if(d.e > 0) war.switch_color(d, color); })
                .on('mouseout', function(d, i) { if(d.e > 0) war.switch_color(d, war.config.cell_color); });
        x = soldier_row.selectAll('.soldier_energy').data(function (d) { return [d]; });
        x.enter()
                .append('td')
                .attr('style', 'padding-left:30px')
                    .append('p')
                    .attr('class', 'soldier_energy')
                    .text(function (d,i) { return d.e; });

        soldier_row.selectAll('.soldier_energy').transition()
                    .text(function(d, i) { return d.e; });
    },

    draw_army_table : function(army_id) {
        var table_container = d3.select('#army' + army_id);
        var table = table_container.append('table').attr('style','padding-bottom:0px');
        var header = table.append('table').attr('class', 'army_table_header');
        var color = army_id == 1 ? war.config.army1_color : war.config.army2_color;
        var name = army_id == 1 ? war.config.army1_name : war.config.army2_name;

        var header_row = header.append('tr');
        header_row.append('td')
                    .append('svg')
                    .attr('width',10)
                    .attr('height',10)
                    .append('circle')
                    .attr('fill', color)
                    .attr('r',10)
                    .attr('cx',1)
                    .attr('cy',5);
        header_row.append('td')
                .attr('style', 'padding-left:10px')
                .append('p')
                .text(name);
    },

    render_actions_and_soldiers : function(action_data, iteration_number) {
        var attacks = 0,
            movements = 0;

        function render_iteration_when_finished() {
            if(!attacks && !movements) {
                war.exploding = false;
                war.render_soldiers_from(iteration_number);
            }
        }

        function distance(d, x, y) {
            return Math.sqrt(Math.pow(d[0] - x, 2) + Math.pow(d[1] - y, 2));
        }
        
        function do_explosion(x, y) {
            var explosion_color = d3.rgb(200,120,20);
            var gx = war.config.gx;
            var gy = war.config.gy;
            war.exploding = true;
            d3.selectAll('.cell')
                .filter(function(d, i) { return x - gx <= d[0] && d[0] <= x + gx && y - gy <= d[1] && d[1] <= y + gy; })
                    .attr('fill', function(d, i) { var dist = distance(d, x, y); return explosion_color.brighter(2 + dist); })
                    .transition()
                    .duration(700)
                    .each("end", function () { attacks--; render_iteration_when_finished(); })
                    .attr('fill', war.config.cell_color);
        }

        var cs = war.svg.selectAll('.soldier').data(action_data, function(d) { return d.name; });
        cs.each(function (d) {
            var cx = war.config.cell_width/2 + (war.config.cell_width + war.config.separation) * d.y;
            var cy = war.config.cell_height/2 + (war.config.cell_height + war.config.separation) * d.x;

            if(d.action == 'A')
            {   
                attacks++;
                war.svg.append("circle")
                        .attr("id", d.name)
                        .attr("class", "grenade")
                        .attr("r", 3)
                        .attr("fill", "olive")
                        .attr("cx", d3.select(this).attr('cx'))
                        .attr("cy", d3.select(this).attr('cy'));
                war.svg.select('#' + d.name)
                        .transition()
                            .each("end", function() { do_explosion(d.x, d.y); })
                            .duration(750)
                            .attr("cx", cx)
                            .attr("cy", cy)
                            .remove();
                
            }
            else if(d.action == 'D')
            {
                movements++;
                d3.select(this)
                    .transition()
                        .duration(750)
                        .each("end", function () { movements--; render_iteration_when_finished(); })
                        .attr("cx", cx)
                        .attr("cy", cy);
            }
        })
    },

    switch_color : function(soldier, color) {
        d3.range(soldier.row - soldier.ry, soldier.row + soldier.ry + 1)
            .forEach( function(row_idx) {
                d3.range(soldier.col - soldier.rx, soldier.col + soldier.rx + 1)
                    .forEach( function(col_idx) {
                        if(row_idx >= 0 && row_idx < war.config.n && col_idx >= 0 && col_idx < war.config.m)
                            d3.select('#r' + row_idx + '_' + col_idx).attr('fill', color);
                    });
            });
    }
}
