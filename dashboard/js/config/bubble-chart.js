// // Global variables
// var chartLayout;
// var trace1;
// var chartData;

// // Function to set up the initial chart
// function setupChart() {
//     fetchChartData().then(data => {
//         let trace1 = {
//             x: data.x || [],   // Use fallback empty array in case `data.x` is undefined
//             y: data.y || [],
//             mode: 'markers',
//             marker: {
//                 size: data.size || []  // Fallback to an empty array if data.size is undefined
//             }
//         };


//         chartLayout = {
//             title: { text: 'Dynamic Marker Size' },
//             showlegend: false,
//             autosize: true,
//             margin: { l: 40, r: 40, t: 40, b: 40 }
//         };

//         // Render the chart for the first time
//         Plotly.newPlot("chart-area-tester", [trace1], chartLayout);
//     });
// }
// setupChart()