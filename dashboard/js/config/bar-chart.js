// function setupBarChart() {
//   var ctx = document.getElementById("myBarChart");
//   if (!ctx) {
//     console.error("Canvas for myBarChart not found!");
//     return null;
//   }
//   return new Chart(ctx, {
//     type: 'bar',
//     data: {
//       labels: [],
//       datasets: []
//     },options: {
//       responsive: true,
//       plugins: {
//           tooltip: {
//               callbacks: {
//                   title: function (tooltipItems) {
//                       // Show the timestamp (date + time) as title
//                       return tooltipItems[0].label;
//                   },
//                   label: function (tooltipItem) {
//                       const datasetLabel = tooltipItem.dataset.label || "";
//                       const value = tooltipItem.raw;
                      
//                       // Get post content from the API response
//                       const postIndex = tooltipItem.dataIndex;
//                       const content = data.contents[postIndex] || "No content available";

//                       // Return multiple lines for tooltip
//                       return [`${datasetLabel}: ${value}`, `Post: ${content}`];
//                   }
//               }
//           }
//       }
//   }
//   });
// }

// function setupBarChart2() {
//   var ctx = document.getElementById("myBarChart2");
//   if (!ctx) {
//     console.error("Canvas for myBarChart2 not found!");
//     return null;
//   }
//   return new Chart(ctx, {
//     type: 'bar',
//     data: {
//       labels: [],
//       datasets: []
//     },options: {
//       responsive: true,
//       plugins: {
//           tooltip: {
//               callbacks: {
//                   title: function (tooltipItems) {
//                       // Show the timestamp (date + time) as title
//                       return tooltipItems[0].label;
//                   },
//                   label: function (tooltipItem) {
//                       const datasetLabel = tooltipItem.dataset.label || "";
//                       const value = tooltipItem.raw;
                      
//                       // Get post content from the API response
//                       const postIndex = tooltipItem.dataIndex;
//                       const content = data.contents[postIndex] || "No content available";

//                       // Return multiple lines for tooltip
//                       return [`${datasetLabel}: ${value}`, `Post: ${content}`];
//                   }
//               }
//           }
//       }
//   }
//   });
// }
