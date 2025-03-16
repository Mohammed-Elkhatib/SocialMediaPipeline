
async function fetchChartData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/chart-data');  // Updated endpoint for virality data
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        
        console.log("Raw data from API:", data);  // Debugging backend response
        return data;
    } catch (error) {
        console.error('Error fetching chart data:', error);
        return null;
    }
}

// Helper function to format numbers as currency
function number_format(value) {
    return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

// Function to set up the initial chart
async function setupChart() {
    try {
        const data = await fetchChartData();  // Fetch virality data from the backend
        
        if (!data) {
            console.error("No data available to render the chart.");
            return;
        }

        // Check the response structure, assuming it follows { x: [], y: [] }
        const xData = data.x;  // Example: Array of dates
        const yData = data.y;  // Example: Array of values

        // Prepare the data for Plotly
        const trace = {
            x: xData,  // X-axis (dates)
            y: yData,  // Y-axis (values)
            type: 'scatter',  // Line chart type
            mode: 'lines+markers',  // Show both lines and markers at data points
            name: 'Virality per Day',
            line: { color: 'rgba(78, 115, 223, 1)' },
            responsive: true, 
        };

        // Layout options (customization)
        const layout = {
            title: 'Virality per Day',
            xaxis: {
                title: 'Date',
                type: 'date',  // Ensures Plotly knows this is a time-based chart
                tickformat: '%Y-%m-%d',  // Format for the date labels
            },
            yaxis: {
                title: 'Virality Value',
            },
            responsive: true, 
        };

        // Plot the chart using Plotly
        Plotly.newPlot('myAreaChart', [trace], layout);

    } catch (error) {
        console.error("Error setting up chart:", error);
    }
}

// Initialize chart
setupChart();
