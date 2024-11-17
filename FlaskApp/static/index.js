$(document).ready(function () {
    // Chartist Graph Class
    class MyCharts {
        constructor(xData, yDataArray) {
            this.xData = xData;
            this.yDataArray = yDataArray;
        }

        createGraph() {
            const data = {
                labels: this.xData,
                series: this.yDataArray
            };

            const options = {
                fullWidth: true,
                showPoint: true,
                lineSmooth: Chartist.Interpolation.cardinal({
                    tension: 0.2 // Creates smoother, curved lines
                }),
                chartPadding: { right: 40 },
                axisX: { showGrid: true, showLabel: true },
                axisY: { offset: 60 }
            };

            const chart = new Chartist.Line('.ct-chart', data, options);

            // Add hover interaction for points
            chart.on('draw', (data) => {
                if (data.type === 'point') {
                    // Add hover event listener
                    const pointNode = data.element._node;
                    pointNode.addEventListener('mouseover', (event) => {
                        const index = data.index;
                        const value = data.value.y;
                        const label = this.xData[index];

                        // Display tooltip
                        this.showTooltip(event, value, label);
                    });

                    // Remove tooltip on mouse out
                    pointNode.addEventListener('mouseout', () => {
                        this.hideTooltip();
                    });
                }
            });
        }

        showTooltip(event, value, label) {
            const tooltip = document.getElementById('hoverTooltip') || this.createTooltip();
            tooltip.innerHTML = `<strong>Value:</strong> ${value}<br><strong>Date:</strong> ${label}`;
            tooltip.style.top = `${event.pageY - 50}px`;
            tooltip.style.left = `${event.pageX + 15}px`;
            tooltip.style.display = 'block'; // Ensure the tooltip is visible
            tooltip.classList.add('show');
        }

        hideTooltip() {
            const tooltip = document.getElementById('hoverTooltip');
            if (tooltip) {
                tooltip.style.display = 'none'; // Hide the tooltip
                tooltip.classList.remove('show');
            }
        }

        createTooltip() {
            const tooltip = document.createElement('div');
            tooltip.id = 'hoverTooltip';
            tooltip.style.position = 'absolute';
            tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.75)';
            tooltip.style.color = 'white';
            tooltip.style.padding = '10px';
            tooltip.style.borderRadius = '5px';
            tooltip.style.pointerEvents = 'none';
            tooltip.style.zIndex = '1000';
            tooltip.style.display = 'none'; // Initially hidden
            document.body.appendChild(tooltip);
            return tooltip;
        }
    }

    // Data for Chartist Graph
    const xData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const yData1 = [10, 20, 15, 30, 25]; // Series 1
    const yData2 = [5, 15, 25, 20, 35];  // Series 2
    const yData3 = [20, 30, 10, 40, 15]; // Series 3

    // Create Chartist Graph
    const chart = new MyCharts(xData, [yData1, yData2, yData3]);
    chart.createGraph();

    
    const playerSlideshow = $('#player-slideshow');
    if (playerSlideshow.length) {
        playerSlideshow.carousel({
            interval: 5000, 
            pause: false    
        });
    }
});
