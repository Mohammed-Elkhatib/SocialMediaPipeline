let chartData1 = null;  // Store chart data globally
let chartData2 = null;

function setupBarChart() {
  var canvas = document.getElementById("myBarChart");
  if (!canvas) {
    console.error("Canvas for myBarChart not found!");
    return null;
  }

  var ctx = canvas.getContext("2d");
  if (!ctx) {
    console.error("Failed to get 2D context for myBarChart!");
    return null;
  }

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: []
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

              if (!chartData1 || !chartData1.contents) {
                return [`${datasetLabel}: ${value}`, "No content available"];
              }

              const postIndex = tooltipItem.dataIndex;
              const content = chartData1.contents[postIndex] || "No content available";

              // Display the tooltip content along with the label and value
              return [`${datasetLabel}: ${value}`, `Post: ${content}`];
            }
          }
        }
      }
    }
  });
}

function setupBarChart2() {
  var canvas = document.getElementById("myBarChart2");
  if (!canvas) {
    console.error("Canvas for myBarChart2 not found!");
    return null;
  }

  var ctx = canvas.getContext("2d");
  if (!ctx) {
    console.error("Failed to get 2D context for myBarChart2!");
    return null;
  }

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: []
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

              if (!chartData2 || !chartData2.contents) {
                return [`${datasetLabel}: ${value}`, "No content available"];
              }

              const postIndex = tooltipItem.dataIndex;
              const content = chartData2.contents[postIndex] || "No content available";

              // Display the tooltip content along with the label and value
              return [`${datasetLabel}: ${value}`, `Post: ${content}`];
            }
          }
        }
      }
    }
  });
}

// Initialize charts
const myBarChart = setupBarChart();
const myBarChart2 = setupBarChart2();

// Fetch and update chart data
async function updateBarChart() {
  if (!myBarChart) {
    console.error("myBarChart is not initialized!");
    return;
  }
  try {
    const response = await fetch('http://127.0.0.1:8000/api/bar-chart-data');
    const data = await response.json();
    console.log("Fetched data:", data); // Debugging

    // Store data globally so tooltips can access it
    myBarChart.data.labels = data.labels;
    myBarChart.data.datasets = data.datasets;
    myBarChart.options.plugins.tooltip.callbacks.label = function (tooltipItem) {
      const datasetLabel = tooltipItem.dataset.label || "";
      const value = tooltipItem.raw;
      
      // Check if contents exist before accessing them
      if (!data.contents || !data.contents[tooltipItem.dataIndex]) {
        return [`${datasetLabel}: ${value}`, "No content available"];
      }

      const content = data.contents[tooltipItem.dataIndex];  
      return [`${datasetLabel}: ${value}`, `Post: ${content}`];
    };

    myBarChart.update();
  } catch (error) {
    console.error("Error fetching chart data:", error);
  }
}


async function updateBarChart2() {
    if (!myBarChart2) {
      console.error("myBarChart is not initialized!");
      return;
    }
    try {
      const response = await fetch('http://127.0.0.1:8000/api/bar-chart-data-likes');
      const data = await response.json();
      console.log("Fetched data:", data); // Debugging
  
      // Store data globally so tooltips can access it
      myBarChart2.data.labels = data.labels;
      myBarChart2.data.datasets = data.datasets;
      myBarChart2.options.plugins.tooltip.callbacks.label = function (tooltipItem) {
        const datasetLabel = tooltipItem.dataset.label || "";
        const value = tooltipItem.raw;
        
        // Check if contents exist before accessing them
        if (!data.contents || !data.contents[tooltipItem.dataIndex]) {
          return [`${datasetLabel}: ${value}`, "No content available"];
        }
  
        const content = data.contents[tooltipItem.dataIndex];  
        return [`${datasetLabel}: ${value}`, `Post: ${content}`];
      };
  
      myBarChart2.update();
    } catch (error) {
      console.error("Error fetching chart data:", error);
    }
  }
  

// Update charts only if they are initialized
if (myBarChart) updateBarChart();
if (myBarChart2) updateBarChart2();
