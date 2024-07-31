const contentDiv = document.getElementById('data-target');
const searchbar = document.querySelector('.search-form')

var emp_data;

function fill_data(data) {
    contentDiv.innerHTML = '';
    val = checkLength(data)
    if (val) {
        data.forEach(item => {
            editRows(item)
        });
    }
}

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const paramValue = urlParams.get('search');

if (paramValue== null) {
    fetch('/employee-data-all')
            .then(response => response.json())
            .then(data => {
                emp_data = data;
                fill_data(data);
            })
            .catch(error => console.error('Error fetching data:', error));
} else {
    fetch(`/employee-data-search/${paramValue}`)
        .then(response => response.json())
        .then(data => {
            emp_data = data;
            fill_data(data);
        })
        .catch(error => console.error('Error fetching data:', error))
}


function editRows(item) {
    const itemDiv = document.createElement('div');
    itemDiv.classList.add('row');

    const firstnametag = document.createElement('p');
    firstnametag.classList.add('part');
    firstnametag.textContent = item['firstname'];

    const lastnametag = document.createElement('p');
    lastnametag.classList.add('part');
    lastnametag.textContent = item['lastname'];

    const img = document.createElement('img');
    img.src = `/uploads/${item['image_path']}`;
    img.classList.add('img-size');
    img.classList.add('part');

    const buttonDivs = document.createElement('div');
    buttonDivs.classList.add('part');
    buttonDivs.classList.add('btn-centre');

    const editButton = document.createElement('button');
    editButton.classList.add('edit-btn');
    editButton.textContent = 'Edit';

    editButton.addEventListener('click', () => {
        window.location.href = `/edit/${item['id']}`
    })

    const deleteButton = document.createElement('button')
    deleteButton.classList.add('delete-btn')
    deleteButton.textContent = 'Delete'

    deleteButton.addEventListener('click', () => {
        emp_data = emp_data.filter(it => it!==item)
        fill_data(emp_data)
        fetch('/edit/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(item['id'])
        });
    })

    buttonDivs.appendChild(editButton)
    buttonDivs.appendChild(deleteButton)

    itemDiv.appendChild(firstnametag)
    itemDiv.appendChild(lastnametag)
    itemDiv.appendChild(img)
    itemDiv.appendChild(buttonDivs)
    contentDiv.appendChild(itemDiv);
}

document.addEventListener('DOMContentLoaded', function() {
    const flashMessage = document.getElementById('temp');
    if (flashMessage) {
        setTimeout(() => {
            flashMessage.style.opacity = '0'; 
                    setTimeout(() => {
                        flashMessage.remove();
                    }, 500);
        }, 5000); 
    }
});

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