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
        const tableData = document.getElementById('tableJson').value;
        try {
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
            console.error('Invalid Table:', e);
            document.getElementById('result').innerText = 'Invalid format';
        }
    }

    function populateTableDropdown() {
        fetch('/tables')
            .then(response => response.json())
            .then(data => {
                const dropdown = document.getElementById('tableName');
                dropdown.innerHTML = ''; // Clear existing options
                data.tables.sort().forEach(table => {
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

    function fetchTableEntries() {
        const tableName = document.getElementById('tableName').value;
        if (tableName) {
            fetch(`/table_entries/${tableName}`)
                .then(response => response.json())
                .then(data => {
                    const entryTableBody = document.getElementById('entryTableBody');
                    entryTableBody.innerHTML = ''; // Clear existing entries
                    data.entries.forEach(entry => {
                        const row = document.createElement('tr');
                        const minRollCell = document.createElement('td');
                        const targetCell = document.createElement('td');
                        // const typeCell = document.createElement('td');

                        const rollRange = entry.min_roll === entry.max_roll ? entry.min_roll : `${entry.min_roll}-${entry.max_roll}`;
                        minRollCell.textContent = rollRange;
                        targetCell.textContent = entry.target;
                        // typeCell.textContent = entry.type;

                        row.appendChild(minRollCell);
                        row.appendChild(targetCell);
                        // row.appendChild(typeCell);

                        entryTableBody.appendChild(row);
                    });
                })
                .catch(error => {
                    console.error('Error fetching table entries:', error);
                    document.getElementById('entryList').innerHTML = 'Error fetching data';
                });
        }
    }

    document.getElementById('tableName').addEventListener('change', fetchTableEntries);

    window.drawFromTable = drawFromTable;
    window.formattedDrawFromTable = formattedDrawFromTable;
});