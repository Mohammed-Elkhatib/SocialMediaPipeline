function updateChart() {
  fetch('http://127.0.0.1:8000/api/chart-update')
      .then(response => response.json())
      .then(data => {
          myLineChart.data.datasets[0].data = data.data;
          myLineChart.update();
      })
      .catch(error => console.error("Error fetching updated data:", error));
}

// Initialize chart and set auto-update every 5 seconds
setupChart();