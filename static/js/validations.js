var storedOTP // global variable to store generated otp value

//function to generate a csrf token for sending a post request through ajax
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      let cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }


// Generate a random OTP
function generateOTP() {
  
    let otp = "";
    let characters = "0123456789";
  
    for (let i = 0; i < 6; i++) {
      otp += characters.charAt(Math.floor(Math.random() * characters.length));
    }

    return otp
}

// Send the OTP to the user's email
function sendOTP(email, otp) {
    document.getElementById("otpInput").style.display='block'
  // Your code to send the OTP to the email address
  $.ajax({
    type: "POST",
    url: "send_otp",
    headers: { "X-CSRFToken": getCookie("csrftoken") },
    data: {
      email: email,
      otp:otp
    },
    success: function(response) {
      
        document.getElementById("email_fail").innerHTML="OTP SENT";
      
    },
    error: function(jqXHR, textStatus, errorThrown) {
        // handle the error, for example display a message that the OTP failed to send
        document.getElementById("email_fail").innerHTML=errorThrown;
      }
  });
 
  // ...
}

// Verify the OTP
function verifyOTP() {
    inputOTP = document.getElementById("otpInput").value
  if (inputOTP === storedOTP) {
    document.getElementById("email_fail").innerHTML="email verified successfully";
    document.getElementById("nextBtn").disabled=false
    document.getElementById("nextBtn").className += " btn btn-success btn-md"
  } else {
    document.getElementById("email_fail").innerHTML="email verification failed";
  }
}
function validate_password(){
    var pass=document.getElementById('password').value;
    var con_pass=document.getElementById('cpwd').value;
    if(pass!=con_pass){
        document.getElementById('match_password').innerHTML='password mismatch';
        document.getElementById('match_password').style.color='red';
        document.getElementById("nextBtn").setAttribute("type", "button")
      
    }else{
        document.getElementById('match_password').innerHTML='password matched';
        document.getElementById('match_password').style.color='green';
        document.getElementById("nextBtn").setAttribute("type", "submit")
    }
}

document.getElementById("verifyEmailButton").addEventListener("click", function() {
    var email = document.getElementById("email").value;
    var otp = generateOTP();
    document.getElementById("verifyEmailButton").innerHTML="Resend OTP";
    document.getElementById("verify_mail").style.display="inline-block";
    sendOTP(email, otp);
    storedOTP = otp;
  
  });