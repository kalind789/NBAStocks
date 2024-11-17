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
                tension: 0.3 // Adjust this value for more or less curve
            }),
            chartPadding: { right: 40 },
            axisX: { showGrid: true, showLabel: true },
            axisY: { offset: 60 }
        };

        const chart = new Chartist.Line('.ct-chart', data, options);

        chart.on('draw', (data) => {
            if (data.type === 'point') {
                data.element._node.addEventListener('mouseover', (event) => {
                    this.showCard(event, data.value.y, data.index);
                });

                data.element._node.addEventListener('mouseout', () => {
                    this.hideCard();
                });
            }
        });
    }

    showCard(event, value, index) {
        const card = document.getElementById('hoverCard');
        card.innerHTML = `Value: ${value}<br>Date: ${this.xData[index]}`;
        card.style.top = `${event.pageY - 40}px`;
        card.style.left = `${event.pageX + 10}px`;
        card.classList.add('show');
    }

    hideCard() {
        const card = document.getElementById('hoverCard');
        card.classList.remove('show');
    }
}

$(document).ready(function () {
    const xData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    const yData1 = [10, 15, 20, 25, 30];
    const yData2 = [5, 10, 15, 20, 25];
    const yData3 = [2, 12, 22, 32, 42];

    const chartInstance = new MyCharts(xData, [yData1, yData2, yData3]);
    chartInstance.createGraph();
});
