const contentDiv = document.getElementById('data-target');
const searchbarButton = document.getElementById('search-button');
const searchbarInput = document.getElementById('search')

// function deleteItem(emp) {
//     const row = document.getElementById(emp)

//     fetch('/edit/delete', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(emp)
//     });
// }

searchbarButton.addEventListener('click', ()=> {
    const text = searchbarInput.value
    fetch(`/employee-attendance-search/${text}`)
        .then(response => response.json())
        .then(data => {
            contentDiv.innerHTML = '';
            data.forEach(item => {
                attendanceRows(item)
            });
        })
        .catch()

});

fetch('/employee-attendance-all')
            .then(response => response.json())
            .then(data => {
                
                contentDiv.innerHTML = '';

                data.forEach(item => {
                    attendanceRows(item)
                });
            })
            .catch(error => console.error('Error fetching data:', error));



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