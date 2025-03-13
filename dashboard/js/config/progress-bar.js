async function createProgressBars() {
    const data = await fetchData();
    
    const container = document.getElementById('progress-container');
    container.innerHTML = ''; // Clear the container before adding new progress bars

    data.forEach(item => {
      const progressCard = document.createElement('div');
      
      // Create label and percentage
      const label = document.createElement('h4');
      label.classList.add('small', 'font-weight-bold');
      label.innerHTML = `${item.label} <span class="float-right">${item.percentage}%</span>`;

      // Create progress bar
      const progressWrapper = document.createElement('div');
      progressWrapper.classList.add('progress', 'mb-4');
      
      const progressBar = document.createElement('div');
      progressBar.classList.add('progress-bar', item.color);
      progressBar.style.width = `${item.percentage}%`;
      progressBar.setAttribute('role', 'progressbar');
      progressBar.setAttribute('aria-valuenow', item.percentage);
      progressBar.setAttribute('aria-valuemin', '0');
      progressBar.setAttribute('aria-valuemax', '100');
      
      // Append label and progress bar to the container
      progressWrapper.appendChild(progressBar);
      progressCard.appendChild(label);
      progressCard.appendChild(progressWrapper);
      
      // Add the progress card to the main container
      container.appendChild(progressCard);
    });
  }