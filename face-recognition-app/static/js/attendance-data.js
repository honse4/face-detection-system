const contentDiv = document.getElementById('data-target');
const searchbar = document.querySelector('.search-form')

function fill_data(data) {
    contentDiv.innerHTML = '';
    val = checkLength(data)
    if (val) {
        data.forEach(item => {
            attendanceRows(item)
        });
    }
}
const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const paramValue = urlParams.get('search');

if (paramValue== null) {
    fetch('/employee-attendance-all')
            .then(response => response.json())
            .then(data => {
                
                fill_data(data)
            })
            .catch(error => console.error('Error fetching data:', error));
} else {
    fetch(`/employee-attendance-search/${paramValue}`)
        .then(response => response.json())
        .then(data => {
            fill_data(data);
        })
        .catch(error => console.error('Error fetching data:', error))
}




function attendanceRows(item) {
    const itemDiv = document.createElement('div');
                    itemDiv.classList.add('row')
                    itemDiv.id = item['id']

    const nametag = document.createElement('p')
    nametag.classList.add('part')
    nametag.textContent = item['name']

    const value = document.createElement('p')
    value.classList.add('part')
    value.textContent = item['length']

    itemDiv.appendChild(nametag)
    itemDiv.appendChild(value)
    contentDiv.appendChild(itemDiv);
}

function checkLength(data) {
    if (data.length == 0) {
        searchbar.style.display = 'none';

        const message = document.createElement('p')
        message.textContent = 'No employees listed here'
        contentDiv.appendChild(message)
        return false
    } else {
        searchbar.style.display = 'flex'
        return true
    }
}