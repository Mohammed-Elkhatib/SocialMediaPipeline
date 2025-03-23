// Global chart data
let chartData1 = null;
let chartData2 = null;
let chartData3 = null;

// Function to setup Plotly Bar Chart
function setupBarChart(divId) {
    var chartDiv = document.getElementById(divId);
    if (!chartDiv) {
        console.error(`Chart div ${divId} not found!`);
        return null;
    }

    var layout = {
        title: 'Top 10 Posts',
        barmode: 'group',
        xaxis: { title: 'Post Date & Time', type: 'category' },
        yaxis: { title: 'Count' },
        hovermode: 'x',  // Ensures tooltips appear on X-axis
        responsive: true
    };

    Plotly.newPlot(divId, [], layout);
}

// Fetch and update chart data
async function updateChartData(chartType) {
    let url = '';
    switch (chartType) {
        case 'comments':
            url = 'http://127.0.0.1:8000/api/bar-chart-data-comments';
            break;
        case 'likes':
            url = 'http://127.0.0.1:8000/api/bar-chart-data-likes';
            break;
        case 'retweets':
            url = 'http://127.0.0.1:8000/api/bar-chart-data-retweets';
            break;
        default:
            console.error("Invalid chart type");
            return;
    }

    try {
        const response = await fetch(url);
        const data = await response.json();

        if (chartType === 'comments') chartData1 = data;
        if (chartType === 'likes') chartData2 = data;
        if (chartType === 'retweets') chartData3 = data;

        const currentChartData = chartType === 'comments' ? chartData1 : 
                                 chartType === 'likes' ? chartData2 : chartData3;

        const postLabels = currentChartData.labels;
        const postContents = currentChartData.datasets[0].content;  // Content is the same across datasets

        // Create traces for Likes, Retweets, and Comments
        const traceLikes = {
            x: postLabels,
            y: currentChartData.datasets[0].data,
            name: "Likes",
            type: 'bar',
            marker: { color: '#4e73df' },
            hovertemplate: '<b>Likes</b>: %{y}<extra></extra>',
            customdata: postContents
        };

        const traceRetweets = {
            x: postLabels,
            y: currentChartData.datasets[1].data,
            name: "Retweets",
            type: 'bar',
            marker: { color: '#1cc88a' },
            hovertemplate: '<b>Retweets</b>: %{y}<extra></extra>',
            customdata: postContents
        };

        const traceComments = {
            x: postLabels,
            y: currentChartData.datasets[2].data,
            name: "Comments",
            type: 'bar',
            marker: { color: '#e74a3b' },
            hovertemplate: '<b>Comments</b>: %{y}<extra></extra>',
            customdata: postContents
        };

        // Invisible scatter trace for showing content on X-axis hover
        const traceHover = {
            x: postLabels,
            y: new Array(postLabels.length).fill(0), // Invisible trace
            text: postContents,
            mode: "markers",
            hoverinfo: "text",
            marker: { opacity: 0 },
            showlegend: false
        };

        const layout = {
            title: `Top 10 ${chartType.charAt(0).toUpperCase() + chartType.slice(1)}`,
            barmode: 'group',
            xaxis: {
                title: 'Post Date & Time',
                tickangle: -20,
                type: 'category',
                tickmode: 'array',
                tickvals: postLabels,
                ticktext: postLabels
            },
            yaxis: { title: 'Count' },
            hovermode: 'x unified', // Unifies tooltips
            hoverlabel: { bgcolor: "#fff", font: { color: "#000" } }
        };

        Plotly.react("myPlotlyChart", [traceLikes, traceRetweets, traceComments, traceHover], layout);

    } catch (error) {
        console.error("Error fetching chart data:", error);
    }
}

// Setup initial chart
setupBarChart("myPlotlyChart");

// Add event listeners for filter buttons
document.getElementById("topCommentsDropdown").addEventListener('click', function() {
    updateChartData('comments');
});

document.getElementById("topLikesDropdown").addEventListener('click', function() {
    updateChartData('likes');
});

document.getElementById("topRetweetsDropdown").addEventListener('click', function() {
    updateChartData('retweets');
});

// Load default data
updateChartData('comments');
