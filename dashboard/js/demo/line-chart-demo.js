async function updateChart(filterBy="date") {
    try {
        const scrollY = window.scrollY; // Save scroll position
        const response = await fetch(`http://127.0.0.1:8000/api/chart-data?filter_by=${filterBy}`);
        const data = await response.json();
        console.log("API Data:", data);  // Debugging line

        if (!data || !data.x || !data.y || data.x.length === 0 || data.y.length === 0) {
            console.warn("No data received for", filterBy);
            document.getElementById("myAreaChart").innerHTML = "<p>No data available</p>";
            return;
        }

        Plotly.react('myAreaChart', [{
            x: data.x,
            y: data.y,
            type: 'scatter',
            mode: 'lines+markers',  // Use 'markers' for individual points
            name: filterBy === "date" ? 'Virality per Day' : 'Virality per Post',
            marker: { color: 'rgba(78, 115, 223, 1)', size: 6 }  // Customize markers
        }], {
            title: filterBy === "date" ? 'Virality Over Time (By Day)' : 'Virality Per Post',
            xaxis: { title: 'Date', type: 'date', tickformat: '%Y-%m-%d %H:%M' },  // Adjust format
            yaxis: { title: 'Virality Score' },
            responsive: true
        });
        window.scrollTo(0, scrollY); // Restore scroll position
    } catch (error) {
        console.error("Error updating chart:", error);
    }
}
updateChart()