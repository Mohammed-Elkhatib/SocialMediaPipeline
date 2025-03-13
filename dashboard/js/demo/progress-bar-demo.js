  // Function to fetch data from the API and update the progress bars
  async function fetchData() {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/progress-data');
      const data = await response.json();

      return data.data;
    } catch (error) {
      console.error("Error fetching data:", error);
      return [];
    }
  }  
  createProgressBars();