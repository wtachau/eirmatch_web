jQuery(function($) {

	function makeAjaxRequest(form, event, onSuccess) {
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
	            if (onSuccess != null) {
	            	onSuccess(data);
	            }
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
		var callback = function(data) {
			jsonData = $.parseJSON(data);
			addTicket(jsonData['postID'], jsonData['image'], jsonData['short'], 
				      jsonData['long'], jsonData['tags'], jsonData['staticURL'], 
				      jsonData['name'], jsonData['email']);
		}
		makeAjaxRequest(this, e, callback);
	});

	// update tags 
	$("#updateTagsForm").submit(function(e)
	{
		makeAjaxRequest(this, e, null);	
	});

	$("#addCommentForm").keypress(function(event) {
	    if (event.which == 13) {
	        event.preventDefault();
	        $("#addCommentForm").submit();
	    }
	});

	// add comment 
	$("#addCommentForm").submit(function(e)
	{
		// add comment to server
		var callback = function(data) {
			// update numComments bubble
			jsonData = $.parseJSON(data);
			console.log(jsonData);
			$(".ticket-"+jsonData['postID']).find('.num_comments').html(jsonData['numComments']);
			// add new box
			addCommentBox(jsonData['userImage'], jsonData['comment']);
			// clear form
			$("#addCommentForm").find("textarea").val("");
		}
		makeAjaxRequest(this, e, callback);
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
	
	var ticketID = "ticket-"+post;
	var ticketSection = $('.'+ticketID);
	// update short description, long description, profile picture, name, emailand tags
	$('#short_description').html(ticketSection.find('.ticket_description').find('.description')[0].innerHTML.trim());
	$('#long_description').html(ticketSection.find('.ticket_description').find('.hidden_description')[0].innerHTML.trim());
	$('#tags_description').html("[ "+ticketSection.find('.tags')[0].innerHTML.trim()+" ]");
	$('#profilepic_big')[0].src = ticketSection.find('img')[0].src;
	$("#contact_me_name").html(ticketSection.find('.ticket_description').find('.hidden_name')[0].innerHTML.trim());
	$("#contact_me").find('a').attr('href', 'mailto:' + ticketSection.find('.ticket_description').find('.hidden_email')[0].innerHTML.trim());
	// update submit form ID property so comments are added to correct Post
	$("#addCommentForm").find('input[name=postID]').val(post);
	// get comments from server
	$.ajax(
	    {
	        url : "getComments",
	        type: "GET",
	        data: {'postID':post},
	        success:function(data, textStatus, jqXHR) 
	        {
	        	// remove previous comments
				$(".comment_box").remove();
	        	// add comments
	            $.each( data, function( num, comment ) {
				  addCommentBox(comment['image'], comment['comment']);
				});
	        },
	        error: function(jqXHR, textStatus, errorThrown) 
	        {
	            alert("Error! Failed response from the server");
	        }
	    });
}

// Add comment
function addCommentBox(userImage, userComment) {
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
}

// Add ticket to the "most recent" pane
function addTicket(postID, image, shortDesc, longDesc, tags, staticURL, name, email) {
	console.log(postID, image, shortDesc, longDesc, tags, staticURL);
	$("#all_posts").prepend("<div class='ticket-"+postID+" ticket_box fade' onclick='showTicket(&quot;"+postID+"&quot;);'>"+
	        		"<table>"+
		        		"<tr>"+
			        		"<td class='ticket_left_half'>"+
				        		"<img class='profilepic_small' src=" +image+ "><br>"+
			        		"</td>"+
			        		"<td class='ticket_description'>"+
			        			"<span class='description'>"+
			        				shortDesc+
			        			"</span>"+
			        			"<span class='hidden_description' style='display:none'>"+
			        				longDesc+
			        			"</span>"+
			        			"<span class='hidden_name' style='display:none'>"+
			        				name+
			        			"</span>"+
			        			"<span class='hidden_email' style='display:none'>"+
			        				email+
			        			"</span>"+
				        		"<div class='tags'>"+
				        			tags+
				        		"</div>"+
			        		"</td>"+
			        		"<td class='ticket_rightview'>"+
			        			"<img class='speechbubble' src='" + staticURL + "img/speechbubble.png'>"+
			        			"<div class='num_comments'>0</div>"+
			        		"</td>"+
		        		"</tr>"+
	        		"</table>"+
	        	"</div>");
}

