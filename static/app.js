document.addEventListener('DOMContentLoaded', function() {
    function drawFromTable() {
        const tableName = document.getElementById('tableName').value;
        fetch(`/draw/${tableName}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerText = `Result: ${data.result}`;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('result').innerText = 'Error fetching data';
            });
    }

    function formattedDrawFromTable() {
        const tableName = document.getElementById('tableName').value;
        fetch(`/formatted_draw/${tableName}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerText = `Formatted Result: ${data.result}`;
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('result').innerText = 'Error fetching data';
            });
    }

    function addTable() {
        const tableJson = document.getElementById('tableJson').value;
        try {
            const tableData = JSON.parse(tableJson);
            fetch('/addTable', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ table: tableData })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('result').innerText = data.message;
                populateTableDropdown(); // Refresh table dropdown after adding a new table
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('result').innerText = 'Error adding table';
            });
        } catch (e) {
            console.error('Invalid JSON:', e);
            document.getElementById('result').innerText = 'Invalid JSON format';
        }
    }

    function populateTableDropdown() {
        fetch('/tables')
            .then(response => response.json())
            .then(data => {
                const dropdown = document.getElementById('tableName');
                dropdown.innerHTML = ''; // Clear existing options
                data.tables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table;
                    option.textContent = table;
                    dropdown.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching tables:', error);
            });
    }

    document.getElementById('addTableForm').addEventListener('submit', function(event) {
        event.preventDefault();
        addTable();
    });

    populateTableDropdown();

    window.drawFromTable = drawFromTable;
    window.formattedDrawFromTable = formattedDrawFromTable;
});