const register_btn = document.getElementById('register_btn');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirm_passwordInput = document.getElementById('confirm-password');
const error_msg = document.getElementById('error');
let valid_pass=false;

register_btn.addEventListener('click', (event) => {
    event.preventDefault(); 

    if (nameInput.value === "" || emailInput.value === "" || passwordInput.value === "" || confirm_passwordInput.value === "") {
        error_msg.textContent = "Please fill all fields.";
        error_msg.style.color = "red";
        error_msg.style.display = 'block';
    } 
    else if (valid_pass==true) {
        if (validateName(nameInput.value) !== "") {
            error_msg.textContent = validateName(nameInput.value);
            error_msg.style.color = "red";
            error_msg.style.display = 'block';
        } 
        else if (validateEmail(emailInput.value) !== "") {
            error_msg.textContent = validateEmail(emailInput.value);
            error_msg.style.color = "red";
            error_msg.style.display = 'block';
        } 
        else if (validatePasswords(passwordInput.value, confirm_passwordInput.value) !== "") {
            error_msg.textContent = validatePasswords(passwordInput.value, confirm_passwordInput.value);
            error_msg.style.color = "red";
            error_msg.style.display = 'block';
        } 
        else {
            error_msg.style.display = 'none';
            alert("Registration successful!");
        }
    }
});


// Validation functions
function validateName(name) {
    if (name.length < 2) {
        return "Name must be at least 2 characters long.";
    } else if (/^\d/.test(name)) {
        return "Name cannot start with a number.";
    }
    return "";
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
        return "Please enter a valid email address.";
    }
    else if(""){
        return "This email address is already in use.";
    }
    else{
        return "";
    }
    
}


function validatePasswords(password, confirmPassword) {
    if (password !== confirmPassword) {
        return "Passwords do not match.";
    }
    return "";
}

passwordInput.addEventListener("input", function() {
    passwordInput.addEventListener("input", updatePasswordStrength);
});

// Function to display password strength feedback
function updatePasswordStrength() {
    const password = passwordInput.value;

    // Check password strength using zxcvbn
    const strength = zxcvbn(password);

    // Update feedback based on the score
    switch (strength.score) {
        case 0:
            error_msg.style.display = 'block';
            error_msg.textContent = "Very Weak";
            error_msg.style.color = "red";
            valid_pass=false;
            break;
        case 1:
            error_msg.style.display = 'block';
            error_msg.textContent = "Weak";
            error_msg.style.color = "orange";
            valid_pass=false;
            break;
        case 2:
            error_msg.style.display = 'block';
            error_msg.textContent = "Strong";
            error_msg.style.color = "yellow";
            valid_pass=false;
            break;
        case 3:
            error_msg.style.display = 'block';
            error_msg.textContent = "Very Strong";
            error_msg.style.color = "darkgreen";
            valid_pass=true;
            break;
    }
}