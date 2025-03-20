function shuffleArray(arr1, arr2) {
    const shuffled1 = [...arr1];
    const shuffled2 = [...arr2];
    for (let i = shuffled1.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        // Swap both word and frequency values together
        [shuffled1[i], shuffled1[j]] = [shuffled1[j], shuffled1[i]];
        [shuffled2[i], shuffled2[j]] = [shuffled2[j], shuffled2[i]];
    }
    return [shuffled1, shuffled2];
}

async function updateBubbleChart() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/hashtag-data');
        let jsonData = await response.json();


        // ✅ Extract the actual array from the response object
        let data = jsonData.data;

        if (!Array.isArray(data)) {
            console.error("Error: 'data' is not an array. Check the backend.");
            return;
        }

        // Extract words and counts
        const words = data.map(item => item.word);
        const frequencies = data.map(item => item.count);
// Shuffle words and frequencies together while keeping correspondence intact
const [shuffledWords, shuffledFrequencies] = shuffleArray(words, frequencies);

// Ensure all frequencies are numbers and not NaN
const validFrequencies = shuffledFrequencies.map(f => !isNaN(f) ? f : 1); // Default to 1 if NaN

// Calculate bubble sizes (scaled from frequencies)
const sizes = validFrequencies.map(f => f*10 ); // Scale up sizes for better visibility

const trace = {
    x: shuffledWords, // Word labels (x-axis)
    y: validFrequencies, // Frequencies (y-axis)
    text: shuffledWords, // Hover text
    mode: 'markers', // Markers for the bubble chart
    marker: {
        size: sizes, // Bubble size based on frequency
        color: validFrequencies, // Color the bubbles based on frequency
        colorscale: 'Viridis', // Color scale
        showscale: true // Show color scale
    }
};

const layout = {
    title: 'Hashtag Frequencies',
    xaxis: {
        title: 'Words',
        type: 'category', // Treat words as categorical data
        categoryorder: 'array', // Prevent Plotly from sorting the words
        tickangle: 45, // Rotate the x-axis labels for better visibility
        tickvals: shuffledWords, // Ensure Plotly uses the shuffled words as ticks
        ticktext: shuffledWords // Ensure the shuffled words are used as labels
    },
    yaxis: {
        title: 'Frequency',
    },
    showlegend: false
};

const chartData = [trace];
Plotly.newPlot('chart-area-tester', chartData, layout);
        // (Rest of your existing logic)
    } catch (error) {
        console.error("Error updating bubble chart:", error);
    }
}
updateBubbleChart();