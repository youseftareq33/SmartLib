const register_btn=document.getElementById('register');
const login_btn=document.getElementById('login');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const error_msg=document.getElementById('error');
let valid_user=false;

// click on register button
register_btn.addEventListener('click',()=>{
   
});

// click on login button
login_btn.addEventListener('click', (event) => {
    event.preventDefault();

    if (emailInput.value === "" || passwordInput.value === "") {
        error_msg.textContent = "Please fill all fields.";
        error_msg.style.color = "red";
        error_msg.style.display = 'block';
    } 
    else if(valid_user==false){
        error_msg.textContent = "Invalid email or password.";
        error_msg.style.color = "red";
        error_msg.style.display = 'block';
    }
    else{
        // enter to home page
    }
});




