const contentDiv = document.getElementById('data-target');
const searchbar = document.querySelector('.search-form');
const time = document.getElementById('time-change')
const label = document.getElementById('label')

function fill_data(data) {
    contentDiv.innerHTML = '';
    val = checkLength(data)
    if (val) {
        data.forEach(item => {
            attendanceRows(item)
        });
    }
}

function getData(paramValue, time) {
        fetch('/employee-attendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                search: paramValue,
                time: time
            })
        })
        .then(response => response.json())
        .then(data => {  
            fill_data(data)
        })
        .catch(error => console.error('Error fetching data:', error));  
}

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const paramValue = urlParams.get('search');
getData(paramValue, 'Month')


function attendanceRows(item) {
    const itemDiv = document.createElement('div');
                    itemDiv.classList.add('row')

    itemDiv.addEventListener('click', function() {
        window.location.href = `/attendance/${item['id']}`
    })

    const nametag = document.createElement('p')
    nametag.classList.add('part')
    nametag.textContent = item['name']

    const percent = document.createElement('p')
    percent.classList.add('part')
    percent.style.paddingLeft = '10%';
    percent.textContent = item['percent']

    const count = document.createElement('p')
    count.classList.add('part')
    count.style.paddingLeft = '10%';
    count.textContent = item['counter']

    itemDiv.appendChild(nametag)
    itemDiv.appendChild(percent)
    itemDiv.appendChild(count)
    contentDiv.appendChild(itemDiv);
}

function checkLength(data) {
    if (data.length == 0) {
        searchbar.style.display = 'none';
        label.style.display = 'none'
        const message = document.createElement('p')
        message.textContent = 'No employees listed here'
        contentDiv.appendChild(message)
        return false
    } else {
        searchbar.style.display = 'flex'
        label.style.display = 'flex'
        return true
    }
}

time.addEventListener('change', function() {
    const val = this.value
    console.log(val)
    const paramValue = urlParams.get('search');
    getData(paramValue, val)
})