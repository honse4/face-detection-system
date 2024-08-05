const dataDiv = document.getElementById('data-target')
id = window.location.pathname.split('/')[2];
const times = ["Week", "Month", "Year", "All"]

fetch(`/attendance/one-employee/${id}`)
.then(response => response.json())
.then(data => {  
    fill_data(data)
})
.catch(error => console.error('Error fetching data:', error));  



function fill_data(data) {
    console.log(data)
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
    timeData(data)
}

function timeData(data) {
    const allCount = data.All.counter
    const allTotal = data.All.total

    const weekCount = data.Week.counter
    const weekTotal = data.Week.total

    const monthCount = data.Month.counter
    const monthTotal = data.Month.total

    const yearCount = data.Year.counter
    const yearTotal = data.Year.total

    const weekDiv = document.createElement('p')
    weekDiv.textContent = weekCount + ' / ' + weekTotal

    const monthDiv = document.createElement('p')
    monthDiv.textContent = monthCount + ' / ' + monthTotal

    const yearDiv = document.createElement('p')
    yearDiv.textContent = yearCount + ' / ' + yearTotal

    const allDiv = document.createElement('p')
    allDiv.textContent = allCount + ' / ' + allTotal

    document.getElementById('week').appendChild(weekDiv)
    document.getElementById('month').appendChild(monthDiv)
    document.getElementById('year').appendChild(yearDiv)
    document.getElementById('all').appendChild(allDiv)
}