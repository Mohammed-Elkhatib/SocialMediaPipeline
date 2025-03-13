// Function to fetch data from the API and update the Word Cloud
async function updateWordCloud() {
  try {
      // Fetch data from the FastAPI backend
      const response = await fetch('http://127.0.0.1:8000/api/language-data');
      const data = await response.json();

      // Process the fetched data into the format required by AnyChart
      const chartData = data.data.map(item => ({
          x: item.word,           // Language name
          value: item.count,   // Population count
          category: item.category // Language family
      }));
      
      // Check if there's an existing chart and dispose it before creating a new one
      if (window.chart) {
          window.chart.dispose();  // Dispose the previous chart to avoid duplication
      }

      // Create a new tag (word) cloud chart
      window.chart = anychart.tagCloud(chartData);

      // Set an array of angles at which the words will be laid out
      window.chart.angles([0, -45, 90]);

      // Enable a color range
      window.chart.colorRange(true);

      window.chart.palette(['blue', 'red']);

      // Set the color range length
      window.chart.colorRange().length('90%');

      // Display the word cloud chart
      window.chart.container("words_container");
      window.chart.draw();

  } catch (error) {
      console.error("Error loading language data:", error);
  }
}

updateWordCloud();
