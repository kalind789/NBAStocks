function viewPortfolio() {
    fetch('/portfolio-data')
        .then(response => response.json())
        .then(data => {
            const portfolioContainer = document.getElementById('portfolioResults');
            portfolioContainer.innerHTML = ''; // Clear existing content

            if (data.length > 0) {
                const table = document.createElement('table');
                table.classList.add('table', 'table-striped', 'table-bordered');

                // Create table header
                const thead = document.createElement('thead');
                thead.innerHTML = `
                    <tr>
                        <th>Player Name</th>
                        <th>Shares</th>
                        <th>Current Value</th>
                        <th>Total Value</th>
                        <th>Fantasy Points (Last 5 Games Average)</th>
                    </tr>
                `;
                table.appendChild(thead);

                const tbody = document.createElement('tbody');

                data.forEach(entry => {
                    const row = document.createElement('tr');
                    row.setAttribute('data-player-id', entry.player_id);

                    row.innerHTML = `
                        <td>${entry.player_name}</td>
                        <td>${entry.shares}</td>
                        <td>$${entry.value.toFixed(2)}</td>
                        <td>$${entry.total_value.toFixed(2)}</td>
                        <td>Loading...</td> <!-- Placeholder for fantasy points -->
                    `;

                    tbody.appendChild(row);

                    // Automatically update player stock value
                    fetch(`/update-player-stock/${entry.player_id}`, { method: 'POST' })
                        .then(() => {
                            // Fetch fantasy points for each player
                            return fetch(`/get_fantasy_points/${entry.player_id}`);
                        })
                        .then(response => response.json())
                        .then(playerData => {
                            if (playerData.status === 'success') {
                                const fantasyPoints = playerData.fantasy_points;
                                row.cells[4].textContent = fantasyPoints.toFixed(2); // Update the "Fantasy Points" cell
                            } else {
                                row.cells[4].textContent = 'N/A'; // Handle missing data
                            }
                        })
                        .catch(error => {
                            row.cells[4].textContent = 'Error'; // Indicate error
                        });
                });

                table.appendChild(tbody);
                portfolioContainer.appendChild(table);
            } else {
                portfolioContainer.textContent = 'Your portfolio is empty.';
            }
        })
        .catch(() => {
            document.getElementById('portfolioResults').textContent = 'Failed to load portfolio.';
        });
}

// Automatically load the portfolio when the page loads
document.addEventListener('DOMContentLoaded', viewPortfolio);
