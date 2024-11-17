// static/search_players.js

// Attach the event listener to prevent page refresh
document.getElementById('searchForm').addEventListener('submit', searchPlayers);
function searchPlayers(event) {
    event.preventDefault(); 

    const query = document.getElementById('searchInput').value;

    // Send GET request to Flask backend
    fetch(`/search-players?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('results');
            resultsContainer.innerHTML = ''; 

            if (data.length > 0) {
                data.forEach(player => {
                    const col = document.createElement('div');
                    col.className = 'col-md-4 mb-3';
                    const card = document.createElement('div');
                    card.className = 'card player-card h-100';

                   
                    card.innerHTML = `
                        <div class="card-body text-center">
                            <h5 class="card-title player-name">${player.full_name}</h5>
                            <p>Fantasy Points: ${player.fantasy_points}</p>
                            <button class="btn btn-warning mt-3">Buy Shares</button>
                        </div>
                    `;
                    card.querySelector('button').onclick = () => handlePlayerClick(player.full_name);
                    col.appendChild(card);
                    resultsContainer.appendChild(col);
                });
            } else {
                resultsContainer.innerHTML = '<p class="text-center text-light">No players found.</p>';
            }
        })
        .catch(error => console.error('Error:', error));
}

function handlePlayerClick(player) {
   
    const shares = prompt(`Enter the number of shares for ${player}:`, "1");
    if (shares === null) {
        
        return;
    }

    const sharesInt = parseInt(shares);
    if (isNaN(sharesInt) || sharesInt <= 0) {
        alert('Please enter a valid number of shares.');
        return;
    }

    
    const data = {
        player_name: player,  
        shares: sharesInt
    };

    
    fetch('/add-portfolio-entry', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                
            } else {
                alert(`Error: ${data.message}`);
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            alert('An unexpected error occurred.');
        });
}
