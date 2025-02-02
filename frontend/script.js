const searchForm = document.getElementById("search-form");
const resultsDiv = document.getElementById("results");
const bookmarksDiv = document.getElementById("bookmarks");
const loginForm = document.getElementById("login-form");
const loginButton = document.getElementById("login-button");
const registerButton = document.getElementById("register-button");
let loggedIn = false;
let authToken = null;

function displayResults(hotels) {
    resultsDiv.innerHTML = "";
    hotels.forEach(hotel => {
        const hotelCard = document.createElement('div');
        hotelCard.classList.add('hotel-card');

        let bestPrice = null;
        let bestPriceSource = null;

        if (hotel.prices.length > 0) {
            bestPrice = hotel.prices[0].price;
            bestPriceSource = hotel.prices[0].source;
            for (let i = 1; i < hotel.prices.length; i++) {
                const price = hotel.prices[i].price;
                if (price < bestPrice) {
                    bestPrice = price;
                    bestPriceSource = hotel.prices[i].source;
                }
            }
        }

        let pricesHtml = '';
        hotel.prices.forEach(priceObj => {
            const isBestPrice = priceObj.price === bestPrice;
            const priceClass = isBestPrice ? 'best-price' : '';
            pricesHtml += `<p> ${priceObj.source}: <span class="${priceClass}">${priceObj.price}</span> </p>`;
        });

        hotelCard.innerHTML = `
            <h3>${hotel.name}</h3>
            <img src="${hotel.image_url}" style="width:200px; height:auto;">
            <p>Star Rating: ${hotel.star_rating}</p>
            <p>Prices: ${pricesHtml}</p>
            <button class="bookmark-button" data-hotel-id="${hotel.id}">Bookmark</button>
            <p><a href="${hotel.booking_url}" target="_blank">Book Now</a></p>
        `;
        resultsDiv.appendChild(hotelCard);
    });

    addBookmarkListeners();
}

function addBookmarkListeners() {
    const bookmarkButtons = document.querySelectorAll('.bookmark-button');
    bookmarkButtons.forEach(button => {
        button.addEventListener('click', async (event) => {
            const hotelId = event.target.getAttribute('data-hotel-id');
            if (loggedIn) {
                try {
                    const response = await fetch('/bookmarks/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Basic ${authToken}`
                        },
                        body: JSON.stringify({ hotel_id: hotelId })
                    });
                    if (response.ok) {
                        fetchBookmarks();
                    } else {
                        const errorData = await response.json();
                        alert("Bookmark was not created: " + errorData.detail);
                    }
                } catch (error) {
                    console.error('Error bookmarking hotel:', error);
                    alert('Failed to bookmark hotel, please try again');
                }
            } else {
                alert('Please login to bookmark a hotel');
            }
        });
    });
}

async function fetchBookmarks() {
    if (loggedIn) {
        try {
            const response = await fetch('/bookmarks/', {
                method: 'GET',
                headers: {
                    'Authorization': `Basic ${authToken}`
                }
            });
            if (response.ok) {
                const bookmarks = await response.json();
                bookmarksDiv.innerHTML = '';
                if (bookmarks.length === 0) {
                    bookmarksDiv.innerHTML = 'No bookmarks yet.';
                } else {
                    bookmarks.forEach(bookmark => {
                        const bookmarkElement = document.createElement('p');
                        bookmarkElement.innerText = `Bookmark ID: ${bookmark.id}, Hotel ID: ${bookmark.hotel_id}`;
                        bookmarksDiv.appendChild(bookmarkElement);
                    });
                }
            } else {
                console.error('Failed to fetch bookmarks');
            }
        } catch (error) {
            console.error('Error fetching bookmarks:', error);
            alert('Failed to fetch bookmarks, please try again.');
        }
    } else {
        bookmarksDiv.innerHTML = "Please login to see your bookmarks.";
    }
}

loginButton.addEventListener('click', async () => {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;
    authToken = btoa(`${username}:${password}`);
    try {
        const response = await fetch('/users/me', {
            method: 'GET',
            headers: {
                'Authorization': `Basic ${authToken}`
            }
        });
        if (response.ok) {
            loggedIn = true;
            alert('Login successful!');
            loginForm.style.display = "none";
            fetchBookmarks();
        } else {
            const errorData = await response.json();
            alert("Login failed: " + errorData.detail);
        }
    } catch (error) {
        console.error('Error logging in:', error);
        alert('Login failed, please try again');
    }
});

registerButton.addEventListener('click', async () => {
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;

    try {
        const response = await fetch('/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username: username, email: email, password: password })
        });
        if (response.ok) {
            alert('Registration successful! Please log in');
        } else {
            const errorData = await response.json();
            alert("Registration failed: " + errorData.detail);
        }
    } catch (error) {
        console.error('Error during registration:', error);
        alert('Registration failed, please try again');
    }
});

searchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const city = document.getElementById("city").value;
    const minPrice = document.getElementById("min_price").value;
    const maxPrice = document.getElementById("max_price").value;
    const starRating = document.getElementById("star_rating").value;

    if (loggedIn) {
        try {
            const response = await fetch('/hotels/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${authToken}`
                },
                body: JSON.stringify({
                    city: city,
                    min_price: minPrice,
                    max_price: maxPrice,
                    star_rating: starRating
                })
            });
            if (response.ok) {
                const hotels = await response.json();
                displayResults(hotels);
            } else {
                const errorData = await response.json();
                alert("Hotel search failed: " + errorData.detail);
            }
        } catch (error) {
            console.error('Error during hotel search:', error);
            alert('Failed to search for hotels, please try again.');
        }
    } else {
        alert('Please login to search hotels.');
    }
});