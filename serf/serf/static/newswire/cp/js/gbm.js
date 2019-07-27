$(function() {

    // Attach a submit handler to the form
    $("#sendForPrint").submit(function(event) {
        // Stop form from submitting normally
        event.preventDefault();
        console.log("send for print clicked!") // sanity check
        $('#sendForPrintButton').addClass("disabled");
        $('#sendForPrintButton').html('<i class="fa fa-paper-plane"></i>&nbsp;Sending...');
            // Get some values from elements on the page:
        var $form = $(this),
            url = $form.attr("action");
        // Send the data using post
        send_bulletin(url);
    });

    // AJAX for sending bulletin
    function send_bulletin(post_url) {
        console.log("send_bulletin triggered!") // sanity check
        $.ajax({
            url: post_url, // the endpoint
            type: "POST", // http method
            data: {
                //the_post: $('#post-text').val()
            }, // data sent with the post request

            // handle a successful response
            success: function(json) {
                $('#sendForPrintButton').html('<i class="fa fa-paper-plane"></i>&nbsp;Sent!'); // remove the value from the input
                //console.log(json); // log the returned json to the console
                console.log("success"); // another sanity check
            },

            // handle a non-successful response
            error: function(xhr, errmsg, err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };

    $('form').on('click', 'button[type=submit]', function(e) {
        $(this.form).data('clicked', this.value);
        console.log("BUTTON VALUE: " + this.value); // another sanity check
    });

    // Approve on submit
    $("body").find('form').filter('[id^=approve-][id$=-form]').on('submit', function(event) {
        event.preventDefault();
        var approval_object_type = $(this).data('clicked').split('-')[1]; // get onject_id
        var approval_object_id = $(this).data('clicked').split('-')[2]; // get onject_id
        console.log("BUTTON ID " + approval_object_type + " " + approval_object_id + " CLICKED"); // another sanity check
        var box = $(this).parents(".box").first();
        approve_object(approval_object_type, approval_object_id, box);
    });

    // AJAX
    function approve_object(approval_object_type, approval_object_id, box) {
        $.ajax({
            url: "/cp/bulletin/under-review/approve/", // the endpoint
            type: "POST", // http method
            data: {
                approval_object_type,
                approval_object_id
            }, // data sent with the post request

            // handle a successful response
            success: function(json) {
                //var bf = box.find('#approved-label-' + approval_object_id);
                var box_body = box.find("#" + approval_object_type + "-box-body-" + approval_object_id);
                var box_footer = box.find("#" + approval_object_type + "-box-footer-" + approval_object_id);
                $('#approved-label-' + approval_object_id).removeClass("hidden")
                if (!$('#' + approval_object_type + '-' + approval_object_id).children().hasClass("fa-plus")) {
                    $('#' + approval_object_type + '-' + approval_object_id).children(".fa-minus").removeClass("fa-minus").addClass("fa-plus");
                    box_body.slideUp();
                    box_footer.slideUp();
                } else {
                    //Convert plus into minus
                    $('#' + approval_object_type + '-' + approval_object_id).children(".fa-plus").removeClass("fa-plus").addClass("fa-minus");
                    box_body.slideDown();
                    box_footer.slideUp();
                }

                console.log(json); // log the returned json to the console
                console.log("success"); // another sanity check
            },

            // handle a non-successful response
            error: function(xhr, errmsg, err) {
                $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: " + errmsg +
                    " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
                console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
            }
        });
    };

    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});
