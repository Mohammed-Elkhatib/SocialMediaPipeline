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

        let data = jsonData.data;

        if (!Array.isArray(data)) {
            console.error("Error: 'data' is not an array. Check the backend.");
            return;
        }

        // Extract words and frequencies
        const words = data.map(item => item.word);
        const frequencies = data.map(item => item.count);

        // Ensure all frequencies are numbers
        const validFrequencies = frequencies.map(f => !isNaN(f) ? f : 1);

        // Scale bubble sizes
        const sizes = validFrequencies.map(f => f * 10);

        const trace = {
            x: words, // Word labels (x-axis)
            y: validFrequencies, // Frequencies (y-axis)
            text: words, // Hover text
            mode: 'markers',
            marker: {
                size: sizes, // Bubble size based on frequency
                color: validFrequencies, // Color the bubbles based on frequency
                colorscale: 'Viridis',
                showscale: true
            }
        };

        const layout = {
            title: 'Hashtag Frequencies',
            xaxis: {
                title: 'Words',
                type: 'category',
                tickangle: 45,
                tickvals: words,
                ticktext: words
            },
            yaxis: {
                title: 'Frequency'
            },
            showlegend: false
        };

        const chartData = [trace];

        // ✅ Efficiently update chart instead of re-creating it
        Plotly.react('chart-area-tester', chartData, layout);
    } catch (error) {
        console.error("Error updating bubble chart:", error);
    }
}
updateBubbleChart();