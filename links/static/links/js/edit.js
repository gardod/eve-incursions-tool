var GROUP_ASSIGN_ORDER = [ "long", "short", "mid" ]
var DRAG_COPY = {
	helper: function() {
        return $(this).clone().removeClass("copy");
    }
};
var DRAG_MOVE = {
	revert: true,
	revertDuration: 0
};

var new_pilot_type;

function get_pilot_copies(pilot_name) {
	return $(".pilot").filter(function() {
		return $(".name", this).text() === pilot_name;
	});
}
function create_pilot(name, type) {
	var group = GROUPS[type];
	// check if new name and in valid ship
	if (name !== "" && get_pilot_copies(name).length === 0 && group !== undefined) {
		var empty_cell = $("."+ group +":empty")[0];
		if (empty_cell !== undefined) {
			var logi = group === "logi";
			var new_element = $("<div>", {
			    "class": type +" pilot draggable "+ (logi ? "move" : "copy"),
			    "data-type": type
			}).append("<span class='name'>"+ name +"</span>");
			$(empty_cell).append(new_element);
			new_element.draggable(logi ? DRAG_MOVE : DRAG_COPY);
		}
	}
}
function get_free_pilots_from_group(group) {
	return $("#table_comp ."+ group +" .pilot").filter(function() {
		var pilot_name = $(".name", this).text();
		var copies = $("#table_links .pilot").filter(function() {
			return $(".name", this).text() === pilot_name;
		});
		// ignore the lines where resebo is set
		for (var i=copies.length-1; i>=0; i--) {
			if ( parseInt( $(".pilot_rsb select", $(copies[i]).closest("tr")).val() ) > 0 ) {
				copies.splice(i, 1);
			}
		}
		return copies.length === 0;
	});
}


$(document).ready(function() {
	/* make forms do nothing */
	$("form").submit(function() {
		return false;
	});
	
	/* config color */
	$(".color").spectrum({
		preferredFormat: "hex6",
		clickoutFiresChange: true,
		showButtons: false,
		change: function(color) {
		    var stylesheet = document.styleSheets[document.styleSheets.length-1],
		    	selector = "." + $(this).closest(".ship_config").data("type"),
		    	rule = "{background-color: "+ color +"}";

			if (stylesheet.insertRule) {
			    stylesheet.insertRule(selector + rule, stylesheet.cssRules.length);
			} else if (stylesheet.addRule) {
			    stylesheet.addRule(selector, rule, -1);
			}
		}
	});

	/* drag and drop */
	$(".draggable.copy").draggable(DRAG_COPY);
	$(".draggable.move").draggable(DRAG_MOVE);
	$(".droppable").droppable({
		drop: function( event, ui ) {
			// copy pilot div - from comp to links
			// new div is movable
			if ( $(ui.draggable).hasClass("copy") ) {
				var new_element = $(ui.draggable).clone();
				$(this).empty();
				$(this).append(new_element);
				new_element.removeClass("copy").addClass("move");
				new_element.draggable(DRAG_MOVE);
			}
			// move pilot div - between links
			else if ( $(ui.draggable).hasClass("move") ) {
				var previous = ui.draggable.parent();
				var replacement = $(this).children();
				$(previous).append(replacement);
				$(this).append(ui.draggable);
			}
		}
	});
	
	/* disable context menu, right click */
	$(".row:not(#toolbar)").on("contextmenu", function(event) {return false;});
	/* remove pilot, right click */
	$("body").on("mousedown", ".pilot", function(event) {
		if (event.which === 3) {
			var copies = get_pilot_copies( $(".name", this).text() );
	        if ( $(this).hasClass("copy") ) {
	        	copies.remove();
	        }
	        else if ( $(this).hasClass("move") ) {
	        	$(copies).removeClass("highlight");
	        	$(this).remove();
	        }
	    }
	});
	
	/* adding pilot */
	$("#table_config").on("click", ".ship_type", function(event) {
		new_pilot_type = $(this).closest(".ship_config").data("type");
		$("#new_pilot_form").show();
		$("#new_pilot_name").focus();
	});
	$("#new_pilot_cancel").on("click", function(event) {
		$("#new_pilot_name").val("");
		$("#new_pilot_form").hide();
	});
	$("#new_pilot_create").on("click", function(event) {
		var new_pilot_name = $("#new_pilot_name").val();
		create_pilot(new_pilot_name, new_pilot_type);
		$("#new_pilot_name").val("");
		$("#new_pilot_form").hide();
	});
	
	/* highlighting pilot */
	$("#table_comp").on("mouseenter", ".pilot.copy", function(event) {
		var copies = get_pilot_copies( $(".name", this).text() );
		$(copies).addClass("highlight");
	}).on("mouseleave", ".pilot.copy", function(event) {
		var copies = get_pilot_copies( $(".name", this).text() );
		$(copies).removeClass("highlight");
	});
	
	/* assigning link */
	$("#table_comp").on("click", ".pilot", function(event) {
		var pilot = $(this);
		var end = false;
		$(".logi .pilot").each(function() {
			logi_row = $(this).closest("tr");
			tl_number = parseInt( $(".pilot_tl select", logi_row).val() );
			for (var i=1; i<=tl_number; i++) {
				// is link available
				tl_cell = $(".pilot_l" + i, logi_row);
				if ( !$(tl_cell).is(':empty') ) { continue; }
				// assign link
				var new_element = $( pilot ).clone();
				$(tl_cell).append(new_element);
				new_element.removeClass("copy").addClass("move");
				new_element.draggable(DRAG_MOVE);
				// exit
				end = true;
				break;
			}
			if ( end ) { return false; }
		});
	});
	
	/* marking basilisk stable */
	$("#table_links").on("click", ".pilot.basilisk", function(event) {
		var pilot = $(this);
		// remove stable
		if ( pilot.hasClass("stable") ){
			pilot.removeClass("stable");
			$(".stable", pilot).remove();
		}
		// add stable
		else {
			pilot.addClass("stable");
			pilot.prepend("<span class='stable'>[S] </span>");
		}
	});
	
	
	/* importing pilots */
	$("#import").on("click", function(event) {
		$("#import_form").show();
		$("#import_comp").focus();
	});
	$("#import_cancel").on("click", function(event) {
		$("#import_comp").val("");
		$("#import_form").hide();
	});
	$("#import_import").on("click", function(event) {
		var input = $("#import_comp").val();
		var wing = $("#import_wing_name").val().toLowerCase();
		var squad = $("#import_ignore_squad").val().toLowerCase();
		var lines, line, name, type, position;
		var pilots = {};
		var pilot_name, found;
		// collect active pilots
		lines = input.split("\n");
		for (var i=0; i<lines.length; i++) {
			line = lines[i].split( /\t| {3,}/ );
			if (line.length === 7) {
				position = line[6].toLowerCase();
				if (position.substring(0, wing.length) === wing) {
					if (squad != "" && position.substring(wing.length+3, wing.length+3+squad.length) == squad) {
						continue;
					}
					name = line[0];
					type = line[2].toLowerCase();
					pilots[name] = type;
				}
			}
		}
		// clear old pilots if not among active anymore
		$("#table_comp .pilot, .logi .pilot").each(function() {
			pilot = $(this);
			found = false;
			$.each( pilots, function(name, type) {
				if ( $(".name", pilot).text() === name && $(pilot).hasClass(type) ) {
					found = true;
					return false;
				}
			});
			if ( !found ) {
				get_pilot_copies( $(".name", pilot).text() ).remove();
			}
		});
		// add new ones
		$.each( pilots, function(name, type) {
			create_pilot(name, type);
		});
		// close popup
		$("#import_comp").val("");
		$("#import_form").hide();
	});
	
	/* auto assigning links */
	/* each pilot once if not linked already */
	$("#assign").on("click", function(event) {
		var logi_row, tl_number, tl_cell;
		var group, group_index=0, index=0, end=false;
		
		group = get_free_pilots_from_group( GROUP_ASSIGN_ORDER[group_index] );
		
		// for every logi for every link
		$(".logi .pilot").each(function() {
			logi_row = $(this).closest("tr");
			tl_number = parseInt( $(".pilot_tl select", logi_row).val() );
			for (var i=1; i<=tl_number; i++) {
				// is link available
				tl_cell = $(".pilot_l" + i, logi_row);
				if ( !$(tl_cell).is(':empty') ) { continue; }
				// find next pilot to link
				while ( !(index < group.length) ) {
					index = 0;
					group_index += 1;
					if ( group_index >= GROUP_ASSIGN_ORDER.length ) {
						// no more unlinked pilots
						end = true;
						break;
					}
					group = get_free_pilots_from_group( GROUP_ASSIGN_ORDER[group_index] );
				}
				if ( end ) { break; }
				// assign link
				var new_element = $(group[index++]).clone();
				$(tl_cell).append(new_element);
				new_element.removeClass("copy").addClass("move");
				new_element.draggable(DRAG_MOVE);
			}
			if ( end ) { return false; }
		});
	});
	
	/* commiting to server */
	$("#commit").on("click", function(event) {
		$("#commit").attr('disabled','disabled');
		// dps is easy
		var dps = {};
		$("#table_comp .pilot").each(function() {
			dps[ $(".name", this).text() ] = $(this).data("type");
		});
		// logi not so much, collecting links
		var logi = {}
		var logi_row, links, tl_cell;
		$(".logi .pilot").each(function() {
			logi_row = $(this).closest("tr");
			links = []
			for (var i=1; i<=4; i++) {
				tl_cell = $(".pilot_l" + i, logi_row);
				if ( $(tl_cell).is(':empty') ) { continue; }
				links.push( $(".pilot .name", tl_cell).text() );
			}
			logi[ $(".name", this).text() ] = {
				"ship_type": $(this).data("type"),
				"tl": parseInt( $(".pilot_tl select", logi_row).val() ),
				"resebo": parseInt( $(".pilot_rsb select", logi_row).val() ),
				"stable": $(this).hasClass("stable"),
				"links": links
			};
		});
		// config
		var config = {};
		$(".ship_config").each(function() {
			config[ $(this).data("type") ] = {
				"color": $(".color", $(this)).val(),
				"script": $(".script", $(this)).val()
			};
		});
		// send post request
		$.post(COMMIT_URL,
			{
				dps: JSON.stringify(dps),
				logi: JSON.stringify(logi),
				config: JSON.stringify(config),
				active_wing: $("#import_wing_name").val(),
				ignore_squad: $("#import_ignore_squad").val()
			},
			function() {
				$("#commit").removeAttr('disabled');
			}
		);
	});
});