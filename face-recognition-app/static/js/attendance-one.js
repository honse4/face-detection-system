const dataDiv = document.getElementById('data-target')
id = window.location.pathname.split('/')[2];

fetch('/attendance/one-employee', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        id: id
    })
})
.then(response => response.json())
.then(data => {  
    fill_data(data)
})
.catch(error => console.error('Error fetching data:', error));  

function fill_data(data) {
    for(const date of data.dates) {
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('row')

        const time = document.createElement('p')
        time.textContent = date
        time.classList.add('part')

        const val = document.createElement('p')
        val.textContent = data['atts'].includes(date) ? 'Present' : 'Absent'
        val.classList.add('part')

        itemDiv.appendChild(time)
        itemDiv.appendChild(val)
        dataDiv.appendChild(itemDiv)
    }
    
}