
/* Functions to actually show or hide popup */
	
var popupStatus = 0;

function loadPopup(popup) { 
	if(popupStatus == 0) { 
		//closeloading(); 
		if (popup == "post") {
			$("#postPopup").fadeIn(0500); 
		} else if (popup == "profile") {
			$("#profilePopup").fadeIn(0500); 
		} else {
			$("#tagPopup").fadeIn(0500); 
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
		$("#tagPopup").fadeOut("normal"); 
		popupStatus = 0;
	}
}

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
		// make server call
		var callback = function(data) {
			jsonData = $.parseJSON(data);
			addTicket("#all_posts", jsonData);
			// then clear forms
			$("#postForm").find('textarea[name=short]')[0].value = "";
			$("#postForm").find('textarea[name=long]')[0].value = "";
			$("#select-tag")[0].selectize.clear();
		}
		makeAjaxRequest(this, e, callback);
	});

	// update tags 
	$("#updateTagsForm").submit(function(e)
	{
		makeAjaxRequest(this, e, function(x) {
			getAllTickets(true)
		});	
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
			$(".ticket-"+jsonData['postID']).find('.num_comments').html(jsonData['numComments']);
			// add new box
			addCommentBox(jsonData['userImage'], jsonData['comment'], jsonData['userFirstName']);
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
	});

	$("#profile_popup_link").click(function() {
		loadPopup("profile");
		return false;
	});

	$(this).keyup(function(event) {
		if (event.which == 27) { // 27 is 'Esc' 
			disablePopup();
		}  	
	});
	
	$("div#backgroundPopup").click(function() {
		disablePopup();
	});

	$("#tagPopup").click(function() {
		disablePopup();
	});
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
	$("#follow_link").attr("onclick","followTicket('"+post+"')");
	// update submit form ID property so comments are added to correct Post
	$("#addCommentForm").find('input[name=postID]').val(post);
	// get comments from server
	getCommentsForPost(post);
}

function getCommentsForPost(post) {
	$.ajax(
    {
        url : "getPostInfo",
        type: "GET",
        data: {'postID':post},
        success:function(data, textStatus, jqXHR) 
        {
        	// remove previous comments
			$(".comment_box").remove();
        	// add comments
            $.each( data['comments'], function( num, comment ) {
			  addCommentBox(comment['image'], comment['comment'], comment['userFirstName']);
			});
			// update "following" button
			updateFollowButton(data['following']);
        },
        error: function(jqXHR, textStatus, errorThrown) 
        {
            alert("Error! Failed response from the server");
        }
    });
}

function getAllTickets(onlyRelevant, callback) {
	$.ajax(
    {
        url : "getAllTickets",
        type: "GET",
        data: {"onlyRelevant":(onlyRelevant==true)},
        success:function(data, textStatus, jqXHR) 
        {
        	var section = onlyRelevant ? "skills" : "all";
        	var sectionID = onlyRelevant ? "#relevant_posts" : "#all_posts";
        	// remove previous tickets
			$(".left_section."+section).find(".ticket_box").remove();

			// add relevant ones
			jsonData = $.parseJSON(data);
        	// add comments
            $.each( jsonData, function( num, ticket ) {
			  addTicket(sectionID, ticket);
			});
			//remove text for no relevant skills
			if (onlyRelevant) {
				if (jsonData.length > 0) {
					$("#no_skills_popup").hide();
				} else {
					$("#no_skills_popup").show();
				}
			}
			if (callback) callback();
        },
        error: function(jqXHR, textStatus, errorThrown) 
        {
            alert("Error! Failed response from the server");
        }
    });
}

// Add comment
function addCommentBox(userImage, userComment, userFirstName) {
	$("#addCommentForm").before("<div class='comment_box'>"+
									"<table style='width: 100%;'>"+
										"<tr>"+
											"<td class='comment_img_box'>"+
												"<img class='comment_img' src="+userImage + "?sz=50>"+
												"<span class='comment_name'>"+ userFirstName + "</span>"+
											"</td>"+
											"<td>"+
												"<span class='comment_text'>"+userComment+"</span>"+
											"</td>"+
										"</tr>"+
									"</table>"+
								"</div>");
}

// Add ticket to the "most recent" pane
function addTicket(htmlElement, ticket) { 

	var tagText = "<div class='tags'>";
	$.each( ticket['tags'], function( i, tag ) {
	  tagText += "<span class='tag_link' onclick='showByTag(&quot;" + tag['id'] + "&quot;);'>"+ tag['name'] + "</span> ";
	});

	$(htmlElement).prepend("<div class='ticket-"+ticket['id']+" ticket_box' onclick='showTicket(&quot;"+ticket['id']+"&quot;);'>"+
	        		"<table class='fade'>"+
		        		"<tr>"+
			        		"<td class='ticket_left_half'>"+
				        		"<img class='profilepic_small' src=" +ticket['image']+ "><br>"+
				        		"<span id='ticket_name'>" + ticket['displayName'] + "</span>"+
			        		"</td>"+
			        		"<td class='ticket_description'>"+
			        			"<span class='description'>"+
			        				ticket['short_description']+
			        			"</span>"+
			        			"<span class='hidden_description' style='display:none'>"+
			        				ticket['long_description']+
			        			"</span>"+
			        			"<span class='hidden_name' style='display:none'>"+
			        				ticket['poster']+
			        			"</span>"+
			        			"<span class='hidden_email' style='display:none'>"+
			        				ticket['email']+
			        			"</span>"+
				        		tagText+
			        		"</td>"+
			        		"<td class='ticket_rightview follow'>"+
			        			"<img "+ (ticket['isFollowed'] ? "" : "style='display:none;' ") + " src='" + ticket['staticURL'] + "img/followcheck.png'>"+
			        		"</td>"+
			        		"<td class='ticket_rightview'>"+
			        			"<img class='speechbubble' src='" + ticket['staticURL'] + "img/speechbubble.png'>"+
			        			"<div class='num_comments'>0</div>"+
			        		"</td>"+
		        		"</tr>"+
	        		"</table>"+
	        	"</div>");
	}

function showByTag(tagID) {
	loadPopup("tag");
	$.ajax(
    {
        url : "getPostsByTag",
        type: "GET",
        data : {'tagID' : tagID},
        success:function(data, textStatus, jqXHR) 
        {
        	// remove previous tickets
			$("#tagPopup").find(".ticket_box").remove();
			jsonData = $.parseJSON(data);
			$("#tagsTitle span").html(jsonData['tagName'])
        	// add comments
            $.each( jsonData['posts'], function( num, ticket ) {
			  addTicket("#tagsList", ticket);
			});
        },
        error: function(jqXHR, textStatus, errorThrown) 
        {
            alert("Error! Failed response from the server");
        }
    });
}

function followTicket(ticketID) {
	// set to loading gif
	$("#follow_link").find("img")[0].src=STATIC_URL+"img/spin.gif";

	// Update follow icons immediately
	var followIcon = $(".ticket-"+ticketID+ " .ticket_rightview.follow img"); 
	$.map($(followIcon), 
		function(val, i) {
			if($(val).css('display') == 'none') {
				$(val).css('display', 'inline');
			} else {
				$(val).css('display', 'none');
			}
		});
	// Now actually update server
	$.ajax(
    {
        url : "follow",
        type: "POST",
        data: {"csrfmiddlewaretoken":$.cookie('csrftoken'),
        		"postID":ticketID},
        success:function(data, textStatus, jqXHR) 
        {
        	// depending on whether user is following/unfollowing, change appearance
        	$("#follow_link img").hide();
        	updateFollowButton(data=="followed");
            
        },
        error: function(jqXHR, textStatus, errorThrown) 
        {
        	$("#follow_link img").hide();
        }
    });
}

// Update the "Follow" button depending if the post is being followed or not
function updateFollowButton(isFollowed) {
	if (isFollowed) {
		$("#follow_link img")[0].src=STATIC_URL+"img/ok.png"; 
		$("#follow_link td")[1].innerHTML = "following"
	} else {
		$("#follow_link img")[0].src=STATIC_URL+"img/follow.png";
		$("#follow_link td")[1].innerHTML = "follow" 
	}
	$("#follow_link img").fadeIn(0500);
	getAllTickets(true);
}



