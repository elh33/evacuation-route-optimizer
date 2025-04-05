// Main JavaScript file for the application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize event listeners
    initLoadCityButton();
});

// Initialize the load city button
function initLoadCityButton() {
    const loadCityBtn = document.getElementById('loadCityBtn');
    if (!loadCityBtn) return;
    
    loadCityBtn.addEventListener('click', function() {
        const citySelect = document.getElementById('citySelect');
        const selectedCity = citySelect.value;
        const loadingSpinner = document.getElementById('loadingSpinner');
        const cityLoadResult = document.getElementById('cityLoadResult');
        
        // Show loading spinner
        loadingSpinner.classList.remove('d-none');
        cityLoadResult.innerHTML = '';
        
        // Load city data
        fetch('/api/load_city', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ city: selectedCity })
        })
        .then(response => response.json())
        .then(data => {
            // Hide loading spinner
            loadingSpinner.classList.add('d-none');
            
            if (data.status === 'success') {
                cityLoadResult.innerHTML = `
                    <div class="alert alert-success">
                        <h5>City Data Loaded Successfully</h5>
                        <p><strong>${selectedCity}</strong> loaded with ${data.nodes.toLocaleString()} nodes and ${data.edges.toLocaleString()} edges.</p>
                        <p class="mb-0">You can now proceed to <a href="/map" class="alert-link">Evacuation Map</a> to find routes.</p>
                    </div>
                `;
            } else {
                cityLoadResult.innerHTML = `
                    <div class="alert alert-danger">
                        <h5>Error Loading City Data</h5>
                        <p>${data.message}</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingSpinner.classList.add('d-none');
            cityLoadResult.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error Loading City Data</h5>
                    <p>An unexpected error occurred. Please try again.</p>
                </div>
            `;
        });
    });
}