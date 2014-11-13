jQuery(function($) {

	function makeAjaxRequest(form, event) {
		//STOP default action
		event.preventDefault();
		var postData = $(form).serializeArray();
	    var formURL = $(form).attr("action");
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
	            console.log(errorThrown + " " + textStatus);    
	        }
	    });
	}

	// Submit post form to server
	$("#postForm").submit(function(e)
	{
		makeAjaxRequest(this, e);
	});

	// update tags 
	$("#updateTagsForm").submit(function(e)
	{
		makeAjaxRequest(this, e);	
	});

	// add comment 
	$("#addCommentForm").submit(function(e)
	{
		makeAjaxRequest(this, e);
		var postData = $(this).serializeArray();
		var userImage;
		var userComment;
		$.each( postData, function( num, data ) {
		  if (data['name'] == "userImage") {
		  	userImage = data['value'];
		  } else if (data['name'] == "comment") {
		  	userComment = data['value'];
		  }
		});
		// clear form
		$("#addCommentForm").find("textarea").val("");
		// add new box
		$("#addCommentForm").before("<div class='comment_box'>"+
							"<table style='width: 100%;'>"+
								"<tr>"+
									"<td class='comment_img_box'>"+
										"<img class='comment_img' src="+userImage+"?sz=50>"+
									"</td>"+
									"<td>"+
										"<span class='comment_text'>"+userComment+"</span>"+
									"</td>"+
								"</tr>"+
							"</table>"+
						"</div>");
	});

	$("#logout").click(function() {
		gapi.auth.signOut();
	    document.location="/logout";
	});

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

