async function updateChart(filterBy = "date") {
    try {
        const response = await fetch(`http://127.0.0.1:8000/api/chart-data?filter_by=${filterBy}`);
        const data = await response.json();
        Plotly.newPlot('myAreaChart', [{
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines+markers',
            name: filterBy === "date" ? 'Virality per Day' : 'Virality per Post',
            marker: { color: 'rgba(78, 115, 223, 1)', size: 6 }
        }], {
            title: filterBy === "date" ? 'Virality Over Time (By Day)' : 'Virality Per Post',
            xaxis: { title: 'Date', type: 'date', tickformat: '%Y-%m-%d %H:%M' },
            yaxis: { title: 'Virality Score' },
            responsive: true
        });
        

    } catch (error) {
        console.error("Error updating chart:", error);
    }
}

updateChart()