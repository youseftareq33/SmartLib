//-----------------------------------------------------
// Dropdown functionality for "Categories"
const categoriesButton = document.getElementById('Categories');
const dropdownCategories = document.getElementById('dropdown-categories');
let closeTimeout_categories; // Declare this variable at the start to handle the timeout properly

// Function to show the dropdown
function showDropdown_categories() {
    clearTimeout(closeTimeout_categories); // Cancel any scheduled closing
    dropdownCategories.style.display = 'block';
    categoriesButton.classList.add('active'); // Add 'active' class to keep the hover color
}

// Function to hide the dropdown with a delay
function hideDropdown_categories() {
    closeTimeout_categories = setTimeout(() => {
        dropdownCategories.style.display = 'none';
        categoriesButton.classList.remove('active'); // Remove 'active' class when hidden
    }, 100); // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
categoriesButton.addEventListener('mouseenter', () => {
    showDropdown_categories();
});

// Event listener for when mouse leaves the categories button
categoriesButton.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the dropdown
    if (!dropdownCategories.contains(event.relatedTarget)) {
        hideDropdown_categories();
    }
});

// Event listener for when mouse enters the dropdown
dropdownCategories.addEventListener('mouseenter', () => {
    showDropdown_categories();
});

// Event listener for when mouse leaves the dropdown
dropdownCategories.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the categories button
    if (!categoriesButton.contains(event.relatedTarget)) {
        hideDropdown_categories();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_categories(category) {
    dropdownCategories.style.display = 'none'; // Hide dropdown after selection
    categoriesButton.classList.remove('active'); // Remove 'active' class after selection
}


//-----------------------------------------------------
// Dropdown functionality for "fav_list"
const fav_list_Button = document.getElementById('fav_list');
const dropdown_fav_list = document.getElementById('fav_list_dropdown');
let closeTimeout_fav_list;
const favListImg = document.getElementById('img_fav_list');  // Correct image element selection

// Function to show the dropdown and change icon color
function showDropdown_fav_list() {
    clearTimeout(closeTimeout_fav_list);  // Cancel any scheduled closing
    dropdown_fav_list.style.display = 'block';
    favListImg.src = 'image/fav_list_yellow.png';  // Change icon to yellow
}

// Function to hide the dropdown with a delay and reset icon color
function hideDropdown_fav_list() {
    closeTimeout_fav_list = setTimeout(() => {
        dropdown_fav_list.style.display = 'none';
        favListImg.src = 'image/fav_list.png';  // Reset icon to original color
    }, 100);  // Delay of 100ms before closing
}

// Event listener for when mouse enters the button
fav_list_Button.addEventListener('mouseenter', () => {
    showDropdown_fav_list();
});

// Event listener for when mouse leaves the button
fav_list_Button.addEventListener('mouseleave', (event) => {
    if (!dropdown_fav_list.contains(event.relatedTarget)) {
        hideDropdown_fav_list();
    }
});

// Event listener for when mouse enters the dropdown
dropdown_fav_list.addEventListener('mouseenter', () => {
    showDropdown_fav_list();
});

// Event listener for when mouse leaves the dropdown
dropdown_fav_list.addEventListener('mouseleave', (event) => {
    if (!fav_list_Button.contains(event.relatedTarget)) {
        hideDropdown_fav_list();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_fav_list(fav_list) {
    dropdown_fav_list.style.display = 'none';  // Hide dropdown after selection
}


//-----------------------------------------------------
// Dropdown functionality for "notification"
const notification_Button = document.getElementById('notification');
const dropdown_notification = document.getElementById('notification_dropdown');
let closeTimeout_notification;  // Declare this variable at the start to handle the timeout properly
const notificationImg = document.getElementById('img_notification');

// Function to show the dropdown
function showDropdown_notification() {
    clearTimeout(closeTimeout_notification);  // Cancel any scheduled closing
    dropdown_notification.style.display = 'block';
    notificationImg.src='image/empty_notification_yellow.png';
}

// Function to hide the dropdown with a delay
function hideDropdown_notification() {
    closeTimeout_notification = setTimeout(() => {
        dropdown_notification.style.display = 'none';
        notificationImg.src='image/empty_notification.png';
    }, 100);  // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
notification_Button.addEventListener('mouseenter', () => {
    showDropdown_notification();
});

// Event listener for when mouse leaves the categories button
notification_Button.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the dropdown
    if (!dropdown_notification.contains(event.relatedTarget)) {
        hideDropdown_notification();
    }
});

// Event listener for when mouse enters the dropdown
dropdown_notification.addEventListener('mouseenter', () => {
    showDropdown_notification();
});

// Event listener for when mouse leaves the dropdown
dropdown_notification.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the categories button
    if (!notification_Button.contains(event.relatedTarget)) {
        hideDropdown_notification();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_notification(notification) {
    dropdown_notification.style.display = 'none';  // Hide dropdown after selection
}

//-----------------------------------------------------
// Dropdown functionality for "user"
const userButton = document.getElementById('user');
const dropdown_user = document.getElementById('dropdown-user');
let closeTimeout_user;  // Declare this variable at the start to handle the timeout properly
const userImg = document.getElementById('img_user');

// Function to show the dropdown
function showDropdown_user() {
    clearTimeout(closeTimeout_user);  // Cancel any scheduled closing
    dropdown_user.style.display = 'block';
    userImg.src = 'image/user_yellow.png';
}

// Function to hide the dropdown with a delay
function hideDropdown_user() {
    closeTimeout_user = setTimeout(() => {
        dropdown_user.style.display = 'none';
        userImg.src = 'image/user.png';
    }, 100);  // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
userButton.addEventListener('mouseenter', () => {
    showDropdown_user();
});

// Event listener for when mouse leaves the categories button
userButton.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the dropdown
    if (!dropdown_user.contains(event.relatedTarget)) {
        hideDropdown_user();
    }
});

// Event listener for when mouse enters the dropdown
dropdown_user.addEventListener('mouseenter', () => {
    showDropdown_user();
});

// Event listener for when mouse leaves the dropdown
dropdown_user.addEventListener('mouseleave', (event) => {
    // Check if the mouse is still inside the categories button
    if (!userButton.contains(event.relatedTarget)) {
        hideDropdown_user();
    }
});

// Function to handle option click in the dropdown
function handleOptionClick_user(option) {
    if (option === 'Send FeedBack') {
        document.getElementById("feedback-stack").style.display = "flex";
    }
}

document.getElementById("closeBtn").onclick = function() {
    document.getElementById("feedback-stack").style.display = "none";
}

window.onclick = function(event) {
    if (event.target === document.getElementById("feedback-stack")) {
        document.getElementById("feedback-stack").style.display = "none";
    }
}

//-----------------------------------------------------
// Stars Rating

const stars = document.querySelectorAll('.star');
const star_num = document.getElementById('star_num');
let timeout_star_num; // Variable to store the timeout ID

stars.forEach((star, index) => {
    // Hover effect
    star.addEventListener('mouseover', function() {
        clearTimeout(timeout_star_num); // Clear any previous timeout
        resetStars();
        highlightStars(index);
        star_num.textContent = (index + 1) + " Stars"; // Update the text inside <p>
    });

    // Remove hover effect when the mouse leaves
    star.addEventListener('mouseout', function() {
        resetStars();
        const activeStars = document.querySelectorAll('.star.active');
        activeStars.forEach((s, i) => highlightStars(i));
        
        if (activeStars.length > 0) {
            star_num.textContent = activeStars.length + " Stars"; // Keep the active star count
        } else {
            // Delay the reset by 0.5 seconds
            timeout_star_num = setTimeout(() => {
                star_num.textContent = ""; // Reset to empty after 0.5s
            }, 180); 
        }
    });

    // Click event to select the rating
    star.addEventListener('click', function() {
        clearTimeout(timeout_star_num); // Clear any previous timeout
        stars.forEach(s => s.classList.remove('active'));
        highlightStars(index);
        stars.forEach((s, i) => {
            if (i <= index) {
                s.classList.add('active');
            }
        });

        const rating = index + 1; // Index starts from 0, so add 1
        console.log("Rating selected: " + rating);
        star_num.textContent = rating + " Stars"; // Update the text after selection
    });
});

// Helper function to highlight stars
function highlightStars(index) {
    for (let i = 0; i <= index; i++) {
        stars[i].style.color = '#FFD700'; // Golden color for highlighted stars
    }
}

// Helper function to reset stars color
function resetStars() {
    stars.forEach(star => {
        star.style.color = '#ddd'; // Reset to grey
    });
}
