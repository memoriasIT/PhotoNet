$("form[name=signup_form").submit(function(e) {

    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
  
    $.ajax({
      url: "/user/signup",
      type: "POST",
      data: data,
      dataType: "json",
      success: function(resp) {
        window.location.href = "/directorio";
      },
      error: function(resp) {
        if (resp.responseJSON.error == undefined) {
          $error.text("An error ocurred").removeClass("error--hidden");
        } else {
          $error.text(resp.responseJSON.error).removeClass("error--hidden");
        }
        
      }
    });
  
    e.preventDefault();
  });
  
  $("form[name=login_form").submit(function(e) {
  
    var $form = $(this);
    var $error = $form.find(".error");
    var data = $form.serialize();
  
    $.ajax({
      url: "/user/login",
      type: "POST",
      data: data,
      dataType: "json",
      success: function(resp) {
        window.location.href = "/directorio";
      },
      error: function(resp) {
        if (resp.responseJSON.error == undefined) {
          $error.text("An error ocurred").removeClass("error--hidden");
        } else {
          $error.text(resp.responseJSON.error).removeClass("error--hidden");
        }
      }
    });
  
    e.preventDefault();
  });