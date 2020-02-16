$(document).ready(function() {
	$("#table_links .logi").on("click", function(event) {
		var row = $(this).parent();
		var was_highlighted = $(row).hasClass("highlighted");
		$("#table_links tr").removeClass("highlighted");
		if ( !was_highlighted ) {
			$(row).addClass("highlighted");
		}
	});
});