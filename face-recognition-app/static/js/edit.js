const contentDiv = document.getElementById('data-target');
const searchbarButton = document.getElementById('search-button');
const searchbarInput = document.getElementById('search')

function deleteItem(emp) {
    const row = document.getElementById(emp)

    fetch('/edit/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(emp)
    });
}

searchbarButton.addEventListener('click', ()=> {
    const text = searchbarInput.value
    fetch(`/employee-data-search/${text}`)
        .then(response => response.json())
        .then(data => {
            contentDiv.innerHTML = '';
            data.forEach(item => {
                editRows(item)
            });
        })
        .catch()

});

fetch('/employee-data-all')
            .then(response => response.json())
            .then(data => {
                
                contentDiv.innerHTML = '';

                data.forEach(item => {
                    editRows(item)
                });
            })
            .catch(error => console.error('Error fetching data:', error));



function editRows(item) {
    const itemDiv = document.createElement('div');
                    itemDiv.classList.add('row')

    const firstnametag = document.createElement('p')
    firstnametag.classList.add('part')
    firstnametag.textContent = item['firstname']

    const lastnametag = document.createElement('p')
    lastnametag.classList.add('part')
    lastnametag.textContent = item['lastname']

    const img = document.createElement('img')
    img.src = `/uploads/${item['image_path']}`
    img.classList.add('img-size')
    img.classList.add('part')

    const buttonDivs = document.createElement('div')
    buttonDivs.classList.add('part')
    buttonDivs.classList.add('btn-centre')

    const editButton = document.createElement('button')
    editButton.classList.add('edit-btn')
    editButton.textContent = 'Edit'

    editButton.addEventListener('click', () => {
        window.location.href = `/edit/${item['id']}`
    })

    const deleteButton = document.createElement('button')
    deleteButton.classList.add('delete-btn')
    deleteButton.textContent = 'Delete'

    deleteButton.addEventListener('click', () => {
        itemDiv.remove()
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
        }, 3000); 
    }
});