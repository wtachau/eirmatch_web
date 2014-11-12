jQuery(function($) {

	/* Listen for events to show or hide popup */

	$("#add_post").click(function() {
		loadPopup("post"); 
		return false;
	});

	$("#add_profile").click(function() {
		loadPopup("profile");
		return false;
	})

	$(this).keyup(function(event) {
		if (event.which == 27) { // 27 is 'Esc' 
			disablePopup();
		}  	
	});
	
	$("div#backgroundPopup").click(function() {
		disablePopup();
	});

	// Submit post form to server
	$("#postForm").submit(function(e)
	{
		var postData = $(this).serializeArray();
	    var formURL = $(this).attr("action");
	    $.ajax(
	    {
	        url : formURL,
	        type: "POST",
	        data : postData,
	        success:function(data, textStatus, jqXHR) 
	        {
	            console.log(data);
	            disablePopup();
	        },
	        error: function(jqXHR, textStatus, errorThrown) 
	        {
	            alert("Error! Failed response from the server");    
	        }
	    });
	    e.preventDefault(); //STOP default action
	});

	$("#logout").click(function() {
		gapi.auth.signOut();
	    document.location="/logout";
	});

	// update tags 
	$("#updateTagsForm").submit(function(e)
	{
		var postData = $(this).serializeArray();
	    var formURL = $(this).attr("action");
	    $.ajax(
	    {
	        url : formURL,
	        type: "POST",
	        data : postData,
	        success:function(data, textStatus, jqXHR) 
	        {
	            console.log(data);
	            disablePopup();
	        },
	        error: function(jqXHR, textStatus, errorThrown) 
	        {
	            alert("Error! Failed response from the server");    
	        }
	    });
	    console.log("Asdf");
	    e.preventDefault(); //STOP default action
	});

	/* Functions to actually show or hide popup */
	
	var popupStatus = 0;
	
	function loadPopup(popup) { 
		if(popupStatus == 0) { 
			//closeloading(); 
			if (popup == "post") {
				$("#postPopup").fadeIn(0500); 
			} else {
				$("#profilePopup").fadeIn(0500); 
			}
			$("#backgroundPopup").css("opacity", "0.7");
			$("#backgroundPopup").fadeIn(0001); 
			popupStatus = 1;
		}	
	}
		
	function disablePopup() {
		if(popupStatus == 1) {
			$("#postPopup").fadeOut("normal");
			$("#profilePopup").fadeOut("normal");  
			$("#backgroundPopup").fadeOut("normal");  
			popupStatus = 0;
		}
	}
});

/* Show tickets */
function showTicket(post) {
	$('#short_description').html($('#'+post).find('.ticket_description').find('.description')[0].innerHTML.trim());
	$('#long_description').html($('#'+post).find('.ticket_description').find('.hidden_description')[0].innerHTML.trim());
	$('#profilepic_big')[0].src = $("#"+post).find('img')[0].src;
}

