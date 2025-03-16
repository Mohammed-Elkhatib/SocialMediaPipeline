// Function to fetch data from the backend
async function fetchChartData() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/bubble-chart-data');
        const data = await response.json();
        
        console.log("Raw data from API:", data);  // Debugging backend response

        return data;
    } catch (error) {
        console.error('Error fetching chart data:', error);
        return null;
    }
}

// Function to set up the initial chart
function setupChart() {
    fetchChartData().then(data => {
        if (!data) {
            console.error('No data available');
            return;
        }

        console.log("Fetched Data:", data);  // Debugging timestamps

        let trace1 = {
            x: data.x.map(ts => new Date(ts * 1000)),  // Convert UNIX timestamps to Date objects
            y: data.y || [],
            mode: 'markers',
            marker: { size: data.size || [] },
            text: data.text || [],
            hoverinfo: 'text'
        };

        const chartLayout = {
            title: { text: 'Engagement vs Date' },
            showlegend: false,
            autosize: true,
            margin: { l: 40, r: 40, t: 40, b: 40 },
            xaxis: {
                title: "Time",
                type: "date",              // Treat x-axis values as dates
                tickformat: "%Y-%m-%d %H:%M", // Format for the date labels
                tickangle: 10
            },
            yaxis: {
                title: 'Engagement',
                rangemode: 'tozero'
            }
        };

        Plotly.newPlot("chart-area-tester", [trace1], chartLayout);
    });
}

// Initialize chart
setupChart();