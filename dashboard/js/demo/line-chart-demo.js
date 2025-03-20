async function fetchChartData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/chart-data');  // Updated endpoint for virality data
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        return data;
    } catch (error) {
        console.error('Error fetching chart data:', error);
        return null;
    }
}

setupChart();
