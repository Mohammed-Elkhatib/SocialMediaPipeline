async function updatePieChart() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/pie-chart-data');
    const data = await response.json();

    // Extract data from the response
    const labels = data.labels;
    const chartData = data.data;

    // Update the chart data dynamically
    myPieChart.data.labels = labels;
    myPieChart.data.datasets[0].data = chartData;

    // Re-render the chart with the new data
    myPieChart.update();
  } catch (error) {
    console.error('Error fetching chart data:', error);
  }
}

// Set up the initial chart
const myPieChart = setupPieChart();
