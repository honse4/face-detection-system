function deleteItem(emp) {
    const row = document.getElementById(emp)
    row.remove()

    fetch('/edit/delete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(emp)
    });
}