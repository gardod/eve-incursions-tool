$(document).ready(function() {
	$(".remove").on("click", function(event) {
		var pilot = $(this).closest(".pilot");
		var pilot_name = $(".name", pilot).text();
		
		$.post(REMOVE_URL,
			{
				name: pilot_name
			},
			function( data ) {
				if ( data == "OK" ) {
					var copies = $(".name").filter(function() {
						return $(this).text() === pilot_name;
					}).closest(".pilot");
					
					copies.remove();
				}
			}
		);
	});
});