// static/portfolio.js

function viewPortfolio() {
    fetch('/portfolio-data')
        .then(response => response.json())
        .then(data => {
            const portfolioContainer = document.getElementById('portfolioResults');
            portfolioContainer.innerHTML = '';

            if (data.length > 0) {
                const table = document.createElement('table');
                table.className = 'table table-dark table-striped table-bordered';
                const thead = table.createTHead();
                const headerRow = thead.insertRow();
                headerRow.innerHTML = `
                    <th>Player Name</th>
                    <th>Shares</th>
                    <th>Current Value</th>
                    <th>Total Value</th>
                `;
                const tbody = table.createTBody();

                data.forEach(entry => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${entry.player_name}</td>
                        <td>${entry.shares}</td>
                        <td>$${entry.value.toFixed(2)}</td>
                        <td>$${entry.total_value.toFixed(2)}</td>
                    `;
                });
                portfolioContainer.appendChild(table);
            } else {
                portfolioContainer.innerHTML = '<p class="text-center text-light">Your portfolio is empty.</p>';
            }
        })
        .catch(error => console.error('Error:', error));
}

// Automatically load the portfolio when the page loads
window.onload = viewPortfolio;