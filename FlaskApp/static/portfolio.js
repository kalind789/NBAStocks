function viewPortfolio() {
    fetch('/portfolio-data')
        .then(response => response.json())
        .then(data => {
            const portfolioContainer = document.getElementById('portfolioResults');
            const chartContainer = document.getElementById('portfolioChart');

            if (!portfolioContainer || !chartContainer) {
                console.error('Portfolio or Chart container not found in the DOM.');
                return;
            }

            portfolioContainer.innerHTML = ''; 
            chartContainer.innerHTML = ''; 

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
                const playersForChart = data.slice(0, 5); // Limit to 5 players for chart
                const chartData = { labels: ['Game 1', 'Game 2', 'Game 3', 'Game 4', 'Game 5'], series: [] };
                const playerNames = [];
                const playerColors = ['#FF5733', '#33FF57', '#3357FF', '#FF33A6', '#FFC733'];

                data.forEach(entry => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${entry.player_name}</td>
                        <td>${entry.shares}</td>
                        <td>$${entry.value.toFixed(2)}</td>
                        <td>$${(entry.value * entry.shares).toFixed(2)}</td>
                        <td id="fantasy-${entry.player_id}">Loading...</td>
                    `;
                    tbody.appendChild(row);

                    // Fetch fantasy points for table
                    fetch(`/get_fantasy_points/${entry.player_id}`)
                        .then(response => response.json())
                        .then(playerData => {
                            if (playerData.status === 'success') {
                                document.getElementById(`fantasy-${entry.player_id}`).textContent = playerData.fantasy_points.toFixed(2);
                            } else {
                                document.getElementById(`fantasy-${entry.player_id}`).textContent = 'N/A';
                            }
                        });

                    // Fetch price history for chart
                    if (playersForChart.includes(entry)) {
                        fetch(`/get_price_history/${entry.player_id}`)
                            .then(response => response.json())
                            .then(priceData => {
                                if (priceData.status === 'success') {
                                    chartData.series.push(priceData.prices);
                                    playerNames.push(entry.player_name);

                                    // Render chart when all player data is fetched
                                    if (chartData.series.length === playersForChart.length) {
                                        loadChart(chartData, playerNames, playerColors);
                                    }
                                }
                            });
                    }
                });

                table.appendChild(tbody);
                portfolioContainer.appendChild(table);
            } else {
                portfolioContainer.textContent = 'Your portfolio is empty.';
            }
        })
        .catch(error => {
            console.error('Error fetching portfolio:', error);
            const portfolioContainer = document.getElementById('portfolioResults');
            portfolioContainer.textContent = 'Failed to load portfolio.';
        });
}

function loadChart(chartData, playerNames) {
    const chartContainer = document.getElementById('portfolioChart');
    const legendContainer = document.getElementById('legendList');

    if (!chartContainer || !legendContainer) {
        console.error('Chart or legend container not found in the DOM.');
        return;
    }

    // Clear the chart and legend containers
    chartContainer.innerHTML = '';
    legendContainer.innerHTML = '';

    // Define a color palette for the lines (and matching legend items)
    const colors = ['#FF0000', '#FFA500', '#FFD700', '#008000', '#0000FF']; // Red, Orange, Gold, Green, Blue

    // Add player names and corresponding colors to the legend
    playerNames.forEach((name, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = name;
        listItem.style.color = colors[index % colors.length]; // Cycle through the color palette
        listItem.style.fontWeight = 'bold';

        // Add a colored circle next to the player's name
        listItem.style.display = 'flex';
        listItem.style.alignItems = 'center';
        const circle = document.createElement('span');
        circle.style.backgroundColor = colors[index % colors.length];
        circle.style.width = '12px';
        circle.style.height = '12px';
        circle.style.borderRadius = '50%';
        circle.style.marginRight = '8px';
        listItem.prepend(circle);

        legendContainer.appendChild(listItem);
    });


    const chart = new Chartist.Line('#portfolioChart', chartData, {
        low: 0,
        high: Math.max(...chartData.series.flat()) + 10,
        showPoint: true,
        lineSmooth: Chartist.Interpolation.simple(),
        axisY: {
            offset: 40,
            labelInterpolationFnc: value => `$${value.toFixed(2)}`
        }
    });

    
    document.querySelectorAll('.ct-series').forEach((series, index) => {
        series.style.stroke = colors[index % colors.length];
    });

    
    chart.on('draw', function (data) {
        if (data.type === 'point') {
            const tooltipCard = document.createElement('div');
            tooltipCard.classList.add('tooltip-card');
            tooltipCard.style.display = 'none';

            
            chartContainer.appendChild(tooltipCard);

            data.element._node.addEventListener('mouseenter', () => {
                const seriesIndex = data.seriesIndex;
                const value = data.value.y;
                const playerName = playerNames[seriesIndex];

                tooltipCard.style.display = 'block';
                tooltipCard.style.left = `${data.x}px`;
                tooltipCard.style.top = `${data.y - 40}px`;
                tooltipCard.innerHTML = `
                    <div><strong>${playerName}</strong></div>
                    <div>Price: $${value.toFixed(2)}</div>
                `;
            });

            data.element._node.addEventListener('mouseleave', () => {
                tooltipCard.style.display = 'none';
            });
        }
    });
}


document.addEventListener('DOMContentLoaded', viewPortfolio);
