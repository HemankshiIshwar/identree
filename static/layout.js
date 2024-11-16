
// Scroll to top when window is loaded
window.onload = function () {
    window.scrollTo(0, 0);
};





// Self developed
// Function to trigger loading animation and music
function triggerLoadingAnimation() {
    // Display loading animation
    $('#loading-container').show();

    // Play the leaves audio
    var loadAudio = document.getElementById('leaves-audio');
    loadAudio.play();

    // Create a timeline for the animation
    var tl = gsap.timeline();

    // Add bird flying animation to the timeline
    tl.fromTo("#bird-animation", { x: -50 }, { x: "100vw", duration: 4, ease: "linear" });

    // Delay for 1 second (1000 milliseconds)
    setTimeout(function () {
        // Hide loading animation
        $('#loading-container').hide();

        // Stop the leaves audio
        loadAudio.pause();
        loadAudio.currentTime = 0;
        $('#bird-animation').hide();

    }, 4000);
}


// Script to share email
var currentActivityId;

function openModal(activityId) {
    currentActivityId = activityId;
    // Open the modal
    $('#shareModal').modal('show');
}

// Email validation function
function validateEmail(email) {
    var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Attach keyup event listener to the email input field
$('#friend_email').on('keyup', function () {
    var emailInput = $(this).val();
    var isValid = validateEmail(emailInput);

    // Display validation feedback
    if (isValid) {
        // Remove any existing error messages
        $('#emailValidationMessage').text('');
    } else {
        $('#emailValidationMessage').text('Please enter a valid email address.');
    }
});


function sendEmail() {
    // Retrieve the activityId from the variable
    var activityId = currentActivityId;

    // Get the email and message from the modal form
    var friendEmail = $('#friend_email').val();
    var message = $('#message').val();
    console.log('activityId:', activityId);

    // Send the data to the server via an AJAX POST request
    $.ajax({
        type: 'POST',
        url: '/share_activity/' + activityId,
        data: { friend_email: friendEmail, message: message },
        success: function (response) {
            // Close the modal
            $('#shareModal').modal('hide');

            // Display a success message using an alert or a custom dialog
            alert('Email sent successfully!');

            //Redirect back to your diary page
            window.location.href = '/mydiary';
        },
        error: function (error) {
            // Handle errors if necessary
            console.error('Error sending email:', error);
        }
    });
}


// Script to intialize map
// Declare a variable to store the map instance
var map = null;

// Function to initialize the map
function initializeMap() {
    map = L.map('map').setView([51.509865, -0.118092], 8);

    // Add OpenStreetMap tiles to the map
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Function to clear the map
function clearMap() {
    if (map) {
        map.off();
        map.remove();
        map = null;
    }
}

// Function to fetch the GBIF taxon key for a given scientific name
async function getTaxonKey(scientificName) {
    const response = await fetch(`https://api.gbif.org/v1/species/match?name=${encodeURIComponent(scientificName)}`);
    const data = await response.json();
    return data.usageKey;
}

// Function to get the user's current location coordinates
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if ('geolocation' in navigator) {
            navigator.geolocation.getCurrentPosition(
                position => {
                    const { latitude, longitude } = position.coords;
                    resolve({ lat: latitude, lng: longitude });
                },
                error => {
                    reject(error);
                }
            );
        } else {
            reject(new Error("Geolocation is not available in this browser."));
        }
    });
}
    
// Self developed
// To load prediction result
$('#upload-form').submit(function (event) {
    event.preventDefault();

    // Trigger loading animation and music
    triggerLoadingAnimation();

    var formData = new FormData(this);
    var imageFile = formData.get("imagefile");

    // Check if no image has been selected
    if (!imageFile) {
        var errorAlert = $('<div>').addClass('alert alert-danger mt-3 mx-auto text-center').attr('id', 'error-alert').text('Please select an image.');
        $('#upload-form').after(errorAlert);
        return;
    }

    // Perform a basic check for valid image formats
    var allowedFormats = ["image/jpeg", "image/png"];
    var selectedImageType = imageFile.type;

    if (!allowedFormats.includes(selectedImageType)) {
        var errorAlert = $('<div>').addClass('alert alert-danger mt-3 mx-auto text-center').attr('id', 'error-alert').text('Invalid image format. Please choose a JPEG or PNG image.');
        $('#upload-form').after(errorAlert);
        return;
    }

    // Fetch result of prediction
    $.ajax({
        type: 'POST',
        url: '/predict',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {

            // Show the result and buttons
            $('#result').append(resultAlert);
            $('#buttons-container').show();

            // Clear any existing result and error messages, and image
            $('#result').empty();
            $('#error-alert-container').empty();
            $('#uploaded-image').remove();

            // Create and display the uploaded image
            var uploadedImage = $('<img>').addClass('mt-3 mx-auto').attr('id', 'uploaded-image').attr('src', URL.createObjectURL(imageFile));
            $('#image-container').show();
            $('#image-container').append(uploadedImage);

            // firstWord = response.class_label.split(' ').slice(0, 1).join(' ');
            class_label = response.class_label;
            sci_name = response.scientific_name;
            o_info = response.other_info;
            c_per = response.confidence_percentage;

            // Create the result alert
            var resultAlert = $('<div>').addClass('alert alert-success mt-3 mx-auto text-center').attr('role', 'alert');

            // Create a link to the Wikipedia page using the first two words
            var wikipediaLink = $('<a>').attr('href', 'https://en.wikipedia.org/wiki/' + sci_name.toLowerCase()).attr('target', '_blank').text('Learn more on Wikipedia');

            // Append the link to the alert
            resultAlert.html('Identified as: ' + class_label + ' (' + c_per + ')' + '<br> Scientific Name: ' + sci_name + '<br> Species Insights: ' + o_info + ' - ');
            resultAlert.append(wikipediaLink);

            // Append the result alert to the result div
            $('#result').append(resultAlert);

            // Scroll to the result
            var resultContainerOffset = $('#result').offset().top;
            $('html, body').animate({
                scrollTop: resultContainerOffset
            }, 90); // Scroll speed

            // Display the hidden buttons with external links
            $('#btn-container').show();

            // Update the URL of the shop button with the resultant tree names
            var nurserylink = "https://www.britishhardwood.co.uk/catalogsearch/result/?q=" + sci_name.replace(/ /g, '+');

            $('#nursery').attr('href', nurserylink).text("Shop " + class_label);

            // Display the hidden maps button
            $("#showMapBtn").css("display", "block");
        },

        error: function (xhr, status, error) {
            // Clear any existing result and uploaded image
            $('#result').empty();
            $('#uploaded-image').remove();
            // Display error message on the webpage
            $('#result').text("An error occurred: " + error);
        }
    });

});


// Event listener when the "Show Map" button is clicked
document.getElementById('showMapBtn').addEventListener('click', async function () {
    var mapContainer = document.getElementById('map');

    // Show the map container
    mapContainer.style.display = 'block';

    // Clear the map if it's already initialized
    clearMap();

    // Initialize the map
    initializeMap();

    // Scroll to the map
    var mapContainerOffset = $('#map').offset().top;
    $('html, body').animate({
        scrollTop: mapContainerOffset
    }, 90);

    // Fetch the GBIF taxon key for the resultant species
    const speciesTaxonKey = await getTaxonKey(sci_name.toLowerCase());

    // Fetch the user's current location coordinates
    try {
        const currentLocation = await getCurrentLocation();
        const userCoordinates = [currentLocation.lat, currentLocation.lng];

        // Set the map's view to the user's current location
        map.setView(userCoordinates, 10); // Zoom level as needed

        // Create a red icon for the user's current location
        const redIcon = L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41]
        });

        // Add a red marker to indicate the user's current location using Leaflet's red marker icon
        L.marker(userCoordinates, { icon: redIcon }).addTo(map);

        let directionsControl; // Declare the directions control variable

        // Fetch tree locations from GBIF API using the taxon key
        fetch(`https://api.gbif.org/v1/occurrence/search?taxonKey=${speciesTaxonKey}`)
            .then(response => response.json())
            .then(data => {
                try {
                    const treeLocations = data.results.map(occurrence => ({
                        lat: occurrence.decimalLatitude,
                        lng: occurrence.decimalLongitude,
                        name: occurrence.scientificName
                    }));

                    if (treeLocations.length === 0) {
                        throw new Error("No tree locations found for this species.");
                    }

                    // Find the closest tree location
                    const closestTreeLocation = findClosestLocation(userCoordinates, treeLocations);

                    // Animate the map to the closest tree location
                    map.flyTo([closestTreeLocation.lat, closestTreeLocation.lng], 10, { animate: true });

                    // Create a green icon for tree markers
                    const greenIcon = L.icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    });

                    // Add markers for tree locations
                    treeLocations.forEach(function (location) {
                        var marker = L.marker([location.lat, location.lng], { icon: greenIcon }).addTo(map);;
                        marker.bindPopup(location.name);
                    });

                } catch (error) {
                    handleMapError(error);
                }
            })
            .catch(error => {
                console.error("Error fetching tree locations:", error);
                handleMapError(error);
            });

    } catch (error) {
        console.error("Error getting current location:", error);
    }

    function handleMapError(error) {
        const mapDiv = document.getElementById("map");
        mapDiv.innerHTML = "An error occurred while handling tree locations: " + error.message;
    }

    function deg2rad(deg) {
        return deg * (Math.PI / 180);
    }

    function calculateDistance(coord1, coord2) {
        const [lat1, lon1] = coord1;
        const [lat2, lon2] = coord2;

        const R = 6371; // Earth's radius in km
        const dLat = deg2rad(lat2 - lat1);
        const dLon = deg2rad(lon2 - lon1);
        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        const distance = R * c;

        return distance;
    }

    function findClosestLocation(userCoordinates, treeLocations) {
        let closestLocation = null;
        let minDistance = Number.POSITIVE_INFINITY;

        treeLocations.forEach(location => {
            const distance = calculateDistance(userCoordinates, [location.lat, location.lng]);
            if (distance < minDistance) {
                minDistance = distance;
                closestLocation = location;
            }
        });

        return closestLocation;
    }



});
