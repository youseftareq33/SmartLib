
//-- Auth Access --

let userId = -1;  
let reader_id=-1;
let user_name="";
let user_rank="";
document.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('jwt_token');

    if (!token) {
        window.location.href = '/login'; // Redirect to login if token is missing
        return;
    }

    try {
        // Decode the JWT token to get the user data
        const decodedToken = jwt_decode(token);
        userId = decodedToken.id; // Extract the user ID

        // Check if the token has expired
        const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
        if (decodedToken.exp < currentTime) {
            // If the token is expired, redirect to login page
            console.error('Token has expired.');
            localStorage.removeItem('jwt_token'); // Remove expired token
            window.location.href = '/login'; // Redirect to login page
            return;
        }
        else {
            // Refresh token before expiration
            const response = await fetch('/refresh-token-api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ token: token })
            });
    
            if (!response.ok) {
                throw new Error('Failed to refresh token');
            }
    
            const data = await response.json();
            localStorage.setItem('jwt_token', data.jwt);
        }

        console.log('User ID:', userId);

        // Check if user_id is available
        if (userId !== -1) {
            fetch(`/get_reader_info?user_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                if (data) {
                    const reader_rank = data.reader_rank;  // Assign the fetched reader_rank
                    reader_id=data.reader_id;
                    document.getElementById('user_rank').textContent = "Rank: " + reader_rank;

                    if(reader_rank=="Rookie"){
                        document.getElementById('img_rank').src = '/static/images/rookie_rank.png'; 
                    }
                    else if(reader_rank=="Bronze"){
                        document.getElementById('img_rank').src = '/static/images/bronze_rank.png'; 
                    }
                    else if(reader_rank=="Silver"){
                        document.getElementById('img_rank').src = '/static/images/silver_rank.png'; 
                    }
                    else if(reader_rank=="Gold"){
                        document.getElementById('img_rank').src = '/static/images/gold_rank.png'; 
                    }

                } else {
                    console.error("Reader not found");
                }
            })
            .catch(error => {
                console.error("Error fetching Reader:", error);
            });
        } 
        else {
            console.log("No user_id found.");
        }

    } catch (error) {
        console.error('Invalid token:', error);
        localStorage.removeItem('jwt_token'); // Remove invalid token
        window.location.href = '/login'; // Redirect to login
    }
});


//---------------------------------------------------------------------------------------

//-- get categories
// Initialize categoriesList as a hash map
const categoriesList = {};

// Fetch categories and dynamically update the UI
const categoriesContainer = document.getElementById('dropdown-categories'); // Ensure this element exists in your HTML

fetch('/getAllCategories/') // Replace with your actual endpoint
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch categories');
        }
        return response.json(); // Parse the JSON response
    })
    .then(categories => {
        // Clear existing content in categoriesContainer
        categoriesContainer.innerHTML = '';

        // Store categories as a hash map and update the UI
        categories.forEach(category => {
            // Populate the hash map
            categoriesList[category.category_id] = category.category_name;

            // Dynamically create and append list items
            const listItem = document.createElement('li');
            listItem.textContent = category.category_name; // Display the category name
            listItem.onclick = () => handleOptionClick_categories(category.category_id);
            categoriesContainer.appendChild(listItem);
        });

        // debug
        // console.log('Categories:', categoriesList);
    })
    .catch(error => {
        console.error('Error fetching categories:', error);
    });

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
    }, 200); // Delay of 100ms before closing
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
function handleOptionClick_categories(category_id) {
    dropdownCategories.style.display = 'none'; // Hide dropdown after selection
    categoriesButton.classList.remove('active'); // Remove 'active' class after selection
    
    localStorage.setItem('selected_category', category_id);
    window.location.href = '/search-page/?search=';
}
//---------------------------------------------------------------------------------------

//-- search --
document.getElementById('search-input').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') { // Check if the pressed key is 'Enter'
        const inputValue = this.value.trim(); // Get the input value and trim whitespace
        if (inputValue != '') {
            const search_input = encodeURIComponent(inputValue);
            const redirectUrl = `/search-page?search=${search_input}`; // Append email to URL
            window.location.href = redirectUrl; // Redirect to confirmation page
        } 

    }
});

//---------------------------------------------------------------------------------------

//-- fav-list --

const fav_list_Button = document.getElementById('fav_list');
const dropdown_fav_list = document.getElementById('fav_list_dropdown');
let closeTimeout_fav_list;
const favListImg = document.getElementById('img_fav_list');  // Correct image element selection

// Function to show the dropdown and change icon color
function showDropdown_fav_list() {
    clearTimeout(closeTimeout_fav_list);  // Cancel any scheduled closing
    dropdown_fav_list.style.display = 'block';
    favListImg.src = '/static/images/fav_list_yellow.png';  // Change icon to yellow
}

// Function to hide the dropdown with a delay and reset icon color
function hideDropdown_fav_list() {
    closeTimeout_fav_list = setTimeout(() => {
        dropdown_fav_list.style.display = 'none';
        favListImg.src = '/static/images/fav_list.png';  // Reset icon to original color
    }, 200);  // Delay of 100ms before closing
}

document.addEventListener('DOMContentLoaded', () => {
    // Event listener for when mouse enters the button
    fav_list_Button.addEventListener('mouseenter', () => {
        showDropdown_fav_list();

        const empty_wishList = document.getElementById('empty_wishList');
        const notEmpty_wishList = document.getElementById('notEmpty_wishList');

        empty_wishList.style.display = 'block';
        notEmpty_wishList.style.display = 'none';

        const wishList_1 = document.getElementById('wishList-item_1');
        const wishList_2 = document.getElementById('wishList-item_2');
        const wishList_3 = document.getElementById('wishList-item_3');
        

        wishList_1.style.display = 'none';
        wishList_2.style.display = 'none';
        wishList_3.style.display = 'none';

        // const notificationList = [
        //     document.getElementById('notifi-item_1'),
        //     document.getElementById('notifi-item_2'),
        //     document.getElementById('notifi-item_3')
        // ];

        
        // notificationList.forEach((notificationElement, index) => {
        //     if (notificationElement) { // Ensure the element exists
        //         notificationElement.addEventListener('click', () => {
        //             window.location.href = `/`; // Example URL
        //         });
        //     }
        // });
        

        // Fetch initial data when page loads
        fetch(`/getLastThreeWishListView?user_id=${userId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch wishList');
                }
                return response.json();
            })
            .then(data => {
                if(Array.isArray(data) && data.length === 0){
                    empty_wishList.style.display = 'block';
                    notEmpty_wishList.style.display = 'none';
                }
                else if(data){
                    empty_wishList.style.display = 'none';
                    notEmpty_wishList.style.display = 'block';

                    data.forEach((wishList, index) => {
                        const wishList_title = document.getElementById(`wishList-item_title_${index + 1}`);
                        const wishList_author = document.getElementById(`wishList-item_author_${index + 1}`);
                        const wishList_category = document.getElementById(`wishList-item_category_${index + 1}`);
                        const wishList_image=document.getElementById(`wishList-item_image_${index + 1}`);
                        const wishList_item = document.getElementById(`wishList-item_${index + 1}`);
                
                        // If there is data for the notification, display the notification item
                        if (wishList) {
                            wishList_item.style.display = 'flex'; // Make the notification item visible

                            // wishList details
                            wishList_title.textContent = wishList.book_name || 'Title...';
                            wishList_author.textContent = `Author: ${wishList.book_author || 'No Author'}`;
                            wishList_category.textContent = `Category: ${wishList.book_type || 'No Category'}`;
                
                            // image
                            if (wishList.book_image) {
                                wishList_image.src = wishList.book_image;
                            }

                            wishList_item.addEventListener('click', () => {
                                window.location.href = `/viewBookPage/${wishList.book_id}`;
                            });
                            
                        } else {
                            // If no data for the wishList, hide the book item
                            wishList_item.style.display = 'none';
                        }
                    });
                    
                }
                
            })
            .catch(error => {
                console.error('Error fetching notification:', error);
            });
        });
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





//---------------------------------------------------------------------------------------

//-- notification --

const notification_Button = document.getElementById('notification');
const dropdown_notification = document.getElementById('notification_dropdown');
let closeTimeout_notification;  // Declare this variable at the start to handle the timeout properly
const notificationImg = document.getElementById('img_notification');

// Function to show the dropdown
function showDropdown_notification() {
    clearTimeout(closeTimeout_notification);  // Cancel any scheduled closing
    dropdown_notification.style.display = 'block';
    notificationImg.src='/static/images/empty_notification_yellow.png';
}

// Function to hide the dropdown with a delay
function hideDropdown_notification() {
    closeTimeout_notification = setTimeout(() => {
        dropdown_notification.style.display = 'none';
        notificationImg.src='/static/images/empty_notification.png';
    }, 200);  // Delay of 100ms before closing
}

// Event listener for when mouse enters the categories button
document.addEventListener('DOMContentLoaded', () => {
    notification_Button.addEventListener('mouseenter', () => {
    showDropdown_notification();
    const empty_notification = document.getElementById('empty_notification');
    const notEmpty_notification = document.getElementById('notEmpty_notification');

    empty_notification.style.display = 'block';
    notEmpty_notification.style.display = 'none';

    const notification_1 = document.getElementById('notifi-item_1');
    const notification_2 = document.getElementById('notifi-item_2');
    const notification_3 = document.getElementById('notifi-item_3');
    

    notification_1.style.display = 'none';
    notification_2.style.display = 'none';
    notification_3.style.display = 'none';

    const notificationList = [
        document.getElementById('notifi-item_1'),
        document.getElementById('notifi-item_2'),
        document.getElementById('notifi-item_3')
    ];

    
    notificationList.forEach((notificationElement, index) => {
        if (notificationElement) { // Ensure the element exists
            notificationElement.addEventListener('click', () => {
                window.location.href = `/`; // Example URL
            });
        }
    });
    

    // Fetch initial data when page loads
    fetch(`/getLastThreeNotificationListView?user_id=${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch notification');
            }
            return response.json();
        })
        .then(data => {
            if(Array.isArray(data) && data.length === 0){
                empty_notification.style.display = 'block';
                notEmpty_notification.style.display = 'none';
            }
            else if(data){
                empty_notification.style.display = 'none';
                notEmpty_notification.style.display = 'block';

                data.forEach((notification, index) => {
                    const notifi_title = document.getElementById(`notifi-item_title_${index + 1}`);
                    const notifi_content = document.getElementById(`notifi-item_content_${index + 1}`);
                    const notifi_image=document.getElementById(`notifi-item_image_${index + 1}`);
                    const notifi_item = document.getElementById(`notifi-item_${index + 1}`);
            
                    // If there is data for the notification, display the notification item
                    if (notification) {
                        notifi_item.style.display = 'flex'; // Make the notification item visible
            
                        // notification notification details
                        notifi_title.textContent = notification.notification_title || 'Title...';
                        notifi_content.textContent = notification.notification_record || 'No content...';
            
                        // image
                        if (notification.notification_title=="Accept Uploaded Book") {
                            notifi_image.src = '/static/images/accept.png'; 
                        }
                        else if(notification.notification_title=="Rejected Uploaded Book"){
                            notifi_image.src = '/static/images/reject.png'; 
                        }
                        else if(notification.notification_title=="New Point Achievement"){
                            notifi_image.src = '/static/images/point.png'; 
                        }
                        
                    } else {
                        // If no data for the notification, hide the book item
                        notifi_item.style.display = 'none';
                    }
                });
                
            }
            
        })
        .catch(error => {
            console.error('Error fetching notification:', error);
        });
    
    });
    
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
//---------------------------------------------------------------------------------------
//-- user --

const userButton = document.getElementById('user');
const dropdown_user = document.getElementById('dropdown-user');
let closeTimeout_user;  // Declare this variable at the start to handle the timeout properly
const userImg = document.getElementById('img_user');

// Function to show the dropdown
function showDropdown_user() {
    clearTimeout(closeTimeout_user);  // Cancel any scheduled closing
    dropdown_user.style.display = 'block';
    userImg.src = '/static/images/user_yellow.png';
}

// Function to hide the dropdown with a delay
function hideDropdown_user() {
    closeTimeout_user = setTimeout(() => {
        dropdown_user.style.display = 'none';
        userImg.src = '/static/images/user.png';
    }, 200);  // Delay of 100ms before closing
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
    if (option === 'Rank') { 
        window.location.href = '/rankPage';
    }
    else if(option === 'User Profile'){
        window.location.href = '/accountSettingsPage';
    }
    else if(option === 'My Uploaded Book'){
        window.location.href = '/myUploadedBookPage';
    }
    else if(option === 'Wish List'){
        window.location.href = '/wish-listPage';
    }
    else if(option === 'Notification'){
        window.location.href = '/notificationPage'; 
    }
    else if(option === 'Send FeedBack'){
        document.getElementById("feedback-stack").style.display = "flex";
    }
    else if(option === 'Log out'){
        localStorage.removeItem('jwt_token'); 
        window.location.href = '/login'; 
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

document.getElementById("sendFeedback").onclick = function() {
    const feedbackText = document.getElementById("feedbackText").value;

    // Ensure userId is set
    if (!userId) {
        alert("User ID is missing. Please log in again.");
        return;
    }

    // Ensure feedback text is not empty
    if (feedbackText.trim() === '') {
        document.getElementById("feedbackText").style.borderColor = "red";
        return;
    }
    else{
        document.getElementById("feedbackText").style.borderColor = "";
    }

    // Log the data to verify it's being sent correctly
    console.log('Sending feedback:', { user_id: userId, feedback_description: feedbackText });

    // Sending feedback to the server via POST request
    fetch('/InsertFeedbackView/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id: userId,
            feedback_description: feedbackText
        }),
    })
    .then(response => response.json())
    .catch(error => {
        console.error("Error sending feedback:", error);
        alert("There was an error sending your feedback.");
    });

    // Close the feedback stack after sending feedback
    document.getElementById("feedback-stack").style.display = "none";
    document.getElementById("feedbackText").value = '';

    document.getElementById("afterfeedback-stack").style.display = "flex";
}

document.getElementById("doneFeedback").onclick = function() {
    document.getElementById("afterfeedback-stack").style.display = "none";
}

document.getElementById("closeBtn2").onclick = function() {
    document.getElementById("afterfeedback-stack").style.display = "none";
}

//---------------------------------------------------------------------------------------
// upload book

upload_book_button=document.getElementById("upload_book");

upload_book_button.addEventListener('mouseenter', () => {
    document.getElementById("upload_book_img").src= '/static/images/after_add_book.png';
    document.getElementById("upload_book_text").style.color="#3f48cc";
});

// Event listener for when mouse leaves the categories button
upload_book_button.addEventListener('mouseleave', (event) => {
    document.getElementById("upload_book_img").src= '/static/images/add_book.png';
    document.getElementById("upload_book_text").style.color="black";
});


upload_book_button.onclick = function() {
    document.getElementById("upload-book-container").style.display = "flex";
}


document.addEventListener("DOMContentLoaded", function () {
    fetchCategories();
});

function fetchCategories() {
    console.log("Fetching categories..."); // Debugging
    fetch("/adminpanel/api/categories/")
        .then(response => {
            console.log("Fetch response status:", response.status); // Debugging
            return response.json();
        })
        .then(data => {
            console.log("Categories data:", data); // Debugging
            const categorySelect = document.getElementById("category");
            categorySelect.innerHTML = '<option value="" disabled selected>Select Category</option>';
            data.categories.forEach(category => {
                const option = document.createElement("option");
                option.value = category.category_id;
                option.textContent = category.category_name;
                categorySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Error fetching categories:", error);
        });
}

document.addEventListener("DOMContentLoaded", fetchCategories);


//-------------------
// Function to open the file input when the drag-and-drop area is clicked
function triggerFileInput() {
    document.getElementById('fileInput').click();
}

// Function to handle file selection
function fileSelected(event) {
    const file = event.target.files[0];
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileSizeLabel = document.getElementById('fileSizeLabel');

    if (file) {
        fileNameDisplay.textContent = file.name;
        fileSizeLabel.textContent = `Size: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
    } else {
        fileNameDisplay.textContent = '';
        fileSizeLabel.textContent = 'No file selected';
    }
}

// Function to trigger image input for book cover
function triggerImageInput(imageInputId) {
    document.getElementById(imageInputId).click();
}

// Function to preview the selected image
function previewImage(event, imagePreviewId) {
    const file = event.target.files[0];
    const imagePreview = document.getElementById(imagePreviewId);

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Function to handle form submission
async function submitForm(event) {
    event.preventDefault();

    const form = document.getElementById('uploadForm');
    const formData = new FormData(form);
    formData.append("reader_id",reader_id);
    try {
        const response = await fetch('insertNewBook/', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            alert(`Error: ${errorText}`);
            return;
        }

        const result = await response.json();
        if (result.status === 'success') {
            closeUploadForm();
        }
        else{
            alert(`Error: Fill all Feild`);
        }
        document.querySelector('main').style.marginTop="0px";
        let alertBox = document.getElementById("gamefication_alert");
            alertBox.style.display = "flex";
        
            setTimeout(() => {
                alertBox.style.display = "none";
                document.querySelector('main').style.marginTop="71px";
            }, 5000); // Hide after 5 seconds
    } catch (error) {
        console.error('Error occurred:', error);
        alert('An unexpected error occurred. Please try again later.');
    }
}

// Function to close the upload modal
function closeUploadForm() {
    const uploadContainer = document.getElementById('upload-book-container');
    uploadContainer.style.display = 'none';

    // Reset the form
    document.getElementById('uploadForm').reset();
    document.getElementById('fileNameDisplay').textContent = '';
    document.getElementById('fileSizeLabel').textContent = 'No file selected';
    document.getElementById('imagePreview1').style.display = 'none';

    // Fetch initial data when page loads
    fetch(`/getUploadedBookListView?user_id=${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch books');
            }
            return response.json();
        })
        .then(data => {
            currentData = data; // Store the fetched data
            updateBookDetails(data); // Update the book details initially

            // Event listener for "Previous" button
            book_prev.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                if (currentData.previous) {
                    curr_url_continue=currentData.previous;
                    loadBooks(curr_url_continue); 
                }
            });

            // Event listener for "Next" button
            book_next.addEventListener('click', (event) => {
                event.preventDefault(); 
                if (currentData.next) {
                    curr_url_continue=currentData.next;
                    loadBooks(curr_url_continue); 
                }
            });
        })
        .catch(error => {
            console.error('Error fetching books:', error);
        });
}


//---------------------------------------------------------------------------------------

// functionality for my book

let currentData = null; 
let curr_url_continue=null;

document.addEventListener('DOMContentLoaded', () => {
    curr_url_continue=`/getUploadedBookListView?user_id=${userId}`;

    const book_prev = document.getElementById('prev');
    const book_next = document.getElementById('next');

    const book_1 = document.getElementById('book_item_1');
    const book_2 = document.getElementById('book_item_2');
    const book_3 = document.getElementById('book_item_3');
    const book_4 = document.getElementById('book_item_4');
    const book_5 = document.getElementById('book_item_5');
    const book_6 = document.getElementById('book_item_6');
    const book_7 = document.getElementById('book_item_7');
    const book_8 = document.getElementById('book_item_8');

    // Initially hide all book items
    book_1.style.display = 'none';
    book_2.style.display = 'none';
    book_3.style.display = 'none';
    book_4.style.display = 'none';
    book_5.style.display = 'none';
    book_6.style.display = 'none';
    book_7.style.display = 'none';
    book_8.style.display = 'none';

    // Fetch initial data when page loads
    fetch(`/getUploadedBookListView?user_id=${userId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch books');
            }
            return response.json();
        })
        .then(data => {
            currentData = data; // Store the fetched data
            updateBookDetails(data); // Update the book details initially

            // Event listener for "Previous" button
            book_prev.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent the default anchor behavior
                if (currentData.previous) {
                    curr_url_continue=currentData.previous;
                    loadBooks(curr_url_continue); 
                }
            });

            // Event listener for "Next" button
            book_next.addEventListener('click', (event) => {
                event.preventDefault(); 
                if (currentData.next) {
                    curr_url_continue=currentData.next;
                    loadBooks(curr_url_continue); 
                }
            });
        })
        .catch(error => {
            console.error('Error fetching books:', error);
        });
});

// Function to load books based on the next or previous URL
function loadBooks(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load books');
            }
            return response.json();
        })
        .then(data => {
            currentData = data; // Update the current data
            updateBookDetails(data); // Update the book details
        })
        .catch(error => {
            console.error('Error loading books:', error);
        });
}

// Function to update book details and pagination buttons
function updateBookDetails(data) {
    const book_prev = document.querySelector('#prev img');
    const book_next = document.querySelector('#next img');

    const book_1 = document.getElementById('book_item_1');
    const book_2 = document.getElementById('book_item_2');
    const book_3 = document.getElementById('book_item_3');
    const book_4 = document.getElementById('book_item_4');
    const book_5 = document.getElementById('book_item_5');
    const book_6 = document.getElementById('book_item_6');
    const book_7 = document.getElementById('book_item_7');
    const book_8 = document.getElementById('book_item_8');

    // Initially hide all book items
    book_1.style.display = 'none';
    book_2.style.display = 'none';
    book_3.style.display = 'none';
    book_4.style.display = 'none';
    book_5.style.display = 'none';
    book_6.style.display = 'none';
    book_7.style.display = 'none';
    book_8.style.display = 'none';

    // Show or hide pagination buttons based on available data
    if (data.previous == null && data.next == null) {
        book_prev.src = '/static/images/prev_page_empty.png';
        book_next.src = '/static/images/next_page_empty.png';
    } else if (data.previous == null && data.next != null) {
        book_prev.src = '/static/images/prev_page_empty.png';
        book_next.src = '/static/images/next_page.png';
    } else if (data.previous != null && data.next == null) {
        book_prev.src = '/static/images/prev_page.png';
        book_next.src = '/static/images/next_page_empty.png';
    } else {
        book_prev.src = '/static/images/prev_page.png';
        book_next.src = '/static/images/next_page.png';
    }

    // Update the book details dynamically
    data.results.forEach((book, index) => {
        const bookName = document.getElementById(`book_name_${index + 1}`);
        const bookAuthor = document.getElementById(`book_author_${index + 1}`);
        const bookCategory = document.getElementById(`book_category_${index + 1}`);
        const bookStatus = document.getElementById(`book_status_${index + 1}`);
        const bookImage = document.getElementById(`book_image_${index + 1}`);
        const bookItem = document.getElementById(`book_item_${index + 1}`);

        // If there is data for the book, display the book item
        if (book) {
            bookItem.style.display = 'block'; // Make the book item visible

            // Update book details
            bookName.textContent = book.book_name || 'No Name';
            bookAuthor.textContent = `Author: ${book.book_author || 'No Author'}`;
            bookCategory.textContent = `Category: ${book.book_type || 'No Category'}`;
            bookStatus.textContent=`Status: ${book.status || 'No Status'}`;

            // Update the image (if available)
            if (book.book_image) {
                bookImage.src = book.book_image;
            }

            bookItem.addEventListener('click', () => {
                window.location.href = `/viewBookPage/${book.book_id}`;
            });

        } else {
            // If no data for the book, hide the book item
            bookItem.style.display = 'none';
        }
    });
}

//---------------------------------------------------------------------------------------

// Functionality for "remove_btn" 

const removeButtons = document.querySelectorAll('[id^="favorite-btn"]'); 
const removeImgs = document.querySelectorAll('[id^="favorite_img"] img');

removeButtons.forEach((removeButtons, index) => {
    removeButtons.addEventListener('click', (event) => {
        event.stopPropagation();
        document.getElementById("alert-stack").style.display = "flex";

        document.getElementById("closeBtn-alert").onclick = function() {
            document.getElementById("alert-stack").style.display = "none";
        }
        
        window.onclick = function(event) {
            if (event.target === document.getElementById("alert-stack")) {
                document.getElementById("alert-stack").style.display = "none";
            }
        }
        
        document.getElementById("alert_delete").onclick = function() {
            // Get the book_id from currentData.results array
            const book = currentData.results[index]; // Access the book object based on the button clicked
            const bookId = book.book_id; // Get the book_id from the currentData

            fetch(`/remove_uploaded_book/?book_id=${bookId}&user_id=${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => {
                if (!response.ok) {
                    console.error(`Error: ${response.status} - ${response.statusText}`);
                    throw new Error('Failed to delete book');
                }
                return response.json();
            })
            .then(data => {
                console.log(data.message || 'Book deleted successfully');
                document.getElementById("alert-stack").style.display = "none";
                updateBooks();
            })
            .catch(error => {
                console.error('Error removing book:', error);
            });
        
        }

        document.getElementById("alert_cancel").onclick = function() {
            document.getElementById("alert-stack").style.display = "none";
        }

        
        
    });
});


function updateBooks(){
    loadBooks(curr_url_continue);
}
