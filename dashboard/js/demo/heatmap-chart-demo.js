async function updateHeatmap() {
    // Fetch data from the FastAPI backend
    const response = await fetch('http://127.0.0.1:8000/api/heatmap-data');
    const data = await response.json();

    // Prepare the data for the Plotly chart
    const heatmapData = [{
        z: data.z,  // Matrix of values for the heatmap
        x: data.x,  // x-axis labels (days)
        y: data.y,  // y-axis labels (times of the day)
        type: 'heatmap',
        hoverongaps: false
    }];
    // Update the chart with the new data
    Plotly.react('heatmapChart', heatmapData);
}
updateHeatmap();