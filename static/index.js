window.onload = function () {
    window.scrollTo(0, 0);
};

document.getElementById("closeButton").addEventListener("click", function () {
    window.location.href = "/";
});

// Get references to form fields
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');

// Add event listeners for keyup events
usernameInput.addEventListener('keyup', validateLoginForm);
passwordInput.addEventListener('keyup', validateLoginForm);

// Function to perform validation
function validateLoginForm() {
    const username = usernameInput.value;
    const password = passwordInput.value;

    // You can add your validation logic here
    // Example: Check if the username and password meet certain criteria

    // For example, check if both fields are not empty
    if (username.trim() !== '' && password.trim() !== '') {
        // Enable the submit button
        document.querySelector('.btn-success[type="submit"]').removeAttribute('disabled');
    } else {
        // Disable the submit button
        document.querySelector('.btn-success[type="submit"]').setAttribute('disabled', 'disabled');
    }
}

// Get references to form fields
const fullnameInput = document.getElementById('fullname');
const emailInput = document.getElementById('email');
const regUsernameInput = document.getElementById('username');
const regPasswordInput = document.getElementById('password');

// Add event listeners for keyup events
fullnameInput.addEventListener('keyup', validateRegistrationForm);
emailInput.addEventListener('keyup', validateRegistrationForm);
regUsernameInput.addEventListener('keyup', validateRegistrationForm);
regPasswordInput.addEventListener('keyup', validateRegistrationForm);

// Function to perform validation
function validateRegistrationForm() {
    const fullname = fullnameInput.value;
    const email = emailInput.value;
    const username = regUsernameInput.value;
    const password = regPasswordInput.value;

    // Regular expression pattern for a valid email
    const emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

    // For example, check if all fields are not empty
    if (fullname.trim() !== '' && email.trim() !== '' && emailPattern.test(email) && username.trim() !== '' && password.trim() !== '') {
        // Enable the submit button
        document.querySelector('.btn-success[type="submit"]').removeAttribute('disabled');
    } else {
        // Disable the submit button
        document.querySelector('.btn-success[type="submit"]').setAttribute('disabled', 'disabled');
    }
}