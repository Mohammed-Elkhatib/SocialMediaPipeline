
// Global chart data
let chartData1 = null;  // Store chart data for top comments
let chartData2 = null;  // Store chart data for top likes
let chartData3 = null;  // Store chart data for top retweets

// Set up Chart.js Bar chart
function setupBarChart(canvasId) {
    var canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas for ${canvasId} not found!`);
        return null;
    }

    var ctx = canvas.getContext("2d");
    if (!ctx) {
        console.error(`Failed to get 2D context for ${canvasId}!`);
        return null;
    }

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [],  // Data labels
            datasets: []  // Chart datasets
        },
        options: {
            responsive: true,
            scales: { 
                y: {
                    beginAtZero: true
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        title: function (tooltipItems) {
                            return tooltipItems[0].label;
                        },
                        label: function (tooltipItem) {
                            const datasetLabel = tooltipItem.dataset.label || "";
                            const value = tooltipItem.raw;

                            // Check which chart data is being used and display accordingly
                            const chartData = chartData1 || chartData2 || chartData3;
                            const postIndex = tooltipItem.dataIndex;
                            const content = chartData?.contents ? chartData.contents[postIndex] : "No content available";

                            return [`${datasetLabel}: ${value}`, `Post: ${content}`];
                        }
                    }
                }
            }
        }
    });
}

// Initialize chart
const myBarChart = setupBarChart("myBarChart");

// Fetch and update chart data based on selected filter
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
        console.log(`Fetched ${chartType} data:`, data);  // Debugging

        // Store data globally so tooltips can access it
        if (chartType === 'comments') {
            chartData1 = data;
        } else if (chartType === 'likes') {
            chartData2 = data;
        } else if (chartType === 'retweets') {
            chartData3 = data;
        }

        // Update chart data
        const currentChartData = chartType === 'comments' ? chartData1 : chartType === 'likes' ? chartData2 : chartData3;

        myBarChart.data.labels = currentChartData.labels;
        myBarChart.data.datasets = currentChartData.datasets;

        // Update tooltips to show correct content
        myBarChart.options.plugins.tooltip.callbacks.label = function (tooltipItem) {
            const datasetLabel = tooltipItem.dataset.label || "";
            const value = tooltipItem.raw;

            const content = currentChartData?.contents ? currentChartData.contents[tooltipItem.dataIndex] : "No content available";

            return [`${datasetLabel}: ${value}`, `Post: ${content}`];
        };

        myBarChart.update();
    } catch (error) {
        console.error("Error fetching chart data:", error);
    }
}

// Event listeners for dropdown items
document.getElementById("topCommentsDropdown").addEventListener('click', function() {
    updateChartData('comments');
});

document.getElementById("topLikesDropdown").addEventListener('click', function() {
    updateChartData('likes');
});

document.getElementById("topRetweetsDropdown").addEventListener('click', function() {
    updateChartData('retweets');
});

// Initial data load
updateChartData('comments');  // Default to "Top Comments" chart data