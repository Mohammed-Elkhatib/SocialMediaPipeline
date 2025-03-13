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
            x: data.x.map(ts => new Date(ts * 1000)),  // ✅ FIX: Convert UNIX timestamps properly
            y: data.y || [],
            mode: 'markers',
            marker: { size: data.size || [] },
            text: data.text || [],
            hoverinfo: 'text'
        };

        const chartLayout = {
            title: { text: 'Virality vs Date' },
            showlegend: false,
            autosize: true,
            margin: { l: 40, r: 40, t: 40, b: 40 },
            xaxis: {
                title: "Time",
                type: "date",  // ✅ FIX: Ensure Plotly treats it as date values
                tickformat: "%Y-%m-%d %H:%M",  // ✅ FIX: Proper date format
                tickangle: 10
            },
            yaxis: {
                title: 'Virality',
                rangemode: 'tozero'
            }
        };

        Plotly.newPlot("chart-area-tester", [trace1], chartLayout);
    });
}

// Initialize chart
setupChart();
