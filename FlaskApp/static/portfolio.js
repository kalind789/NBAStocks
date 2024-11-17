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
                        <th>Fantasy Points</th>
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
                        <td>$<span id="value-${entry.player_id}">${entry.value.toFixed(2)}</span></td>
                        <td>$<span id="total-${entry.player_id}">${entry.total_value.toFixed(2)}</span></td>
                        <td id="fantasy-${entry.player_id}">Loading...</td>
                    `;
                    tbody.appendChild(row);

                    // Fetch fantasy points and update the stock price for this player
                    fetch(`/get_fantasy_points/${entry.player_id}`)
                        .then(response => response.json())
                        .then(playerData => {
                            if (playerData.status === 'success') {
                                const fantasyPoints = playerData.fantasy_points;

                                // Update fantasy points in the table
                                document.getElementById(`fantasy-${entry.player_id}`).textContent = fantasyPoints.toFixed(2);

                                // Update player stock price
                                fetch(`/update-player-stock/${entry.player_id}`, { method: 'POST' })
                                    .then(() => {
                                        // Re-fetch portfolio data to get the updated value
                                        fetch(`/portfolio-data`)
                                            .then(response => response.json())
                                            .then(updatedData => {
                                                const updatedPlayer = updatedData.find(p => p.player_id === entry.player_id);
                                                if (updatedPlayer) {
                                                    document.getElementById(`value-${entry.player_id}`).textContent = updatedPlayer.value.toFixed(2);
                                                    document.getElementById(`total-${entry.player_id}`).textContent = (updatedPlayer.value * entry.shares).toFixed(2);
                                                }
                                            });
                                    })
                                    .catch(error => console.error(`Error updating stock for player ${entry.player_id}:`, error));
                            } else {
                                document.getElementById(`fantasy-${entry.player_id}`).textContent = 'N/A';
                            }
                        })
                        .catch(error => {
                            console.error(`Error fetching fantasy points for player ID ${entry.player_id}:`, error);
                            document.getElementById(`fantasy-${entry.player_id}`).textContent = 'Error';
                        });
                });

                table.appendChild(tbody);
                portfolioContainer.appendChild(table);

                // Render Chartist.js chart for the first five players
                loadChart(data.slice(0, 5));
            } else {
                portfolioContainer.textContent = 'Your portfolio is empty.';
            }
        })
        .catch(error => {
            console.error('Error fetching portfolio:', error);
            document.getElementById('portfolioResults').textContent = 'Failed to load portfolio.';
        });
}

function loadChart(players) {
    const chartContainer = document.querySelector('.ct-chart');
    const labels = ['Game 1', 'Game 2', 'Game 3', 'Game 4', 'Game 5']; // Labels for the games
    const series = []; // Series for the chart

    let completedRequests = 0;

    players.forEach(player => {
        fetch(`/get_fantasy_points/${player.player_id}`)
            .then(response => response.json())
            .then(playerData => {
                if (playerData.status === 'success') {
                    // Extract last 5 game prices (ensure it's an array)
                    const last5Prices = Object.values(playerData.average_stats || {}).slice(0, 5);
                    
                    // Push the last 5 prices into the series array
                    series.push(last5Prices);

                    completedRequests++;
                    if (completedRequests === players.length) {
                        // All player data loaded, render the chart
                        new Chartist.Line(chartContainer, {
                            labels: labels,
                            series: series
                        }, {
                            low: 0,
                            showArea: true,
                            fullWidth: true,
                            chartPadding: {
                                right: 40
                            }
                        });
                    }
                }
            })
            .catch(error => console.error(`Error fetching chart data for player ID ${player.player_id}:`, error));
    });
}


// Automatically load the portfolio and chart when the page loads
document.addEventListener('DOMContentLoaded', viewPortfolio);
