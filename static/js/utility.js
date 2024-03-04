function populate_suggestions_datalist() {
    fetch('/suggest_classes')
            .then(response => response.json())
            .then(data => {
                // Update the datalist options
                const datalist = document.getElementById('datalistOptions');
                datalist.innerHTML = '';

                // Populate datalist with options from the backend
                data.forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option;
                    datalist.appendChild(optionElement);
                });
            })
            .catch(error => console.error('Error fetching data:', error));
}