function populate_suggestions_triple(selectedOption) {
    fetch(`/query_builder?selectedOption=${encodeURIComponent(selectedOption)}`)
        .then(response => response.json())
        .then(data => {
            const select1 = document.getElementById('select1');
            const select2 = document.getElementById('select2');
            const select3 = document.getElementById('select3');

            let currentSelect;
            let keys;

            if (select1.value === '') {
                keys = Object.keys(data);
                currentSelect = select1;
            } else if (select2.value === '') {
                keys = Object.keys(data[select1.value]);
                currentSelect = select2;
            } else {
                keys = data[select1.value][select2.value];
                currentSelect = select3;
            }

            currentSelect.innerHTML = '';

            for (let i = 0; i < keys.length; i++) {
                const newOption = document.createElement('option');
                const optionText = document.createTextNode(keys[i]);
                newOption.appendChild(optionText);
                newOption.setAttribute('value', keys[i]);
                currentSelect.appendChild(newOption);
            }
        })
        .catch(error => console.error('Error fetching data:', error));
}

function showSelectFields() {
    const select1 = document.getElementById("select1");
    const select2 = document.getElementById("select2");
    const select3 = document.getElementById("select3");

    if (select1.value !== "") {
        select2.classList.remove("d-none");
    } else {
        select2.classList.add("d-none");
    }

    if (select2.value !== "") {
        select3.classList.remove("d-none");
    } else {
        select3.classList.add("d-none");
    }
}

function clearSelectedOptions() {
        document.getElementById("select1").selectedIndex = -1;
        document.getElementById("select2").selectedIndex = -1;
        document.getElementById("select3").selectedIndex = -1;
    }

    // Event listener for modal close event
    $('#exampleModalCenter').on('hidden.bs.modal', function (e) {
        clearSelectedOptions();
        showSelectFields()
    });
//Should be used to implement filtering the graph ?
function filter() {

}