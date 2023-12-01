function showTableWithFilters(tableName) {
    const tables = ["fornecedores", "clientes", "vendas", "produtos"];

    tables.forEach(table => {
        const filtersElement = document.getElementById(`${table}-filters`);
        const tableElement = document.getElementById(`${table}-table`);

        if (table === tableName) {
            filtersElement.style.display = "block";
            tableElement.style.display = "none";
        } else {
            filtersElement.style.display = "none";
            tableElement.style.display = "none";
        }
    });

    fetchTableData(`/get_table_data/${tableName}`, `${tableName}-table`);
}

function applyFiltersAndFetchData(tableName) {
    const filters = {};

    document.querySelectorAll(`#${tableName}-filters input`).forEach(input => {
        filters[input.name] = input.value;
    });

    fetchTableData(`/get_table_data/${tableName}`, `${tableName}-table`, filters);
}

function fetchTableData(endpoint, tableId, filters=null) {
    const config = filters ? {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(filters)
    } : {};

    fetch(endpoint, config)
        .then(response => response.text())
        .then(data => {
            const tableElement = document.getElementById(tableId);
            tableElement.innerHTML = data;
            tableElement.style.display = "block";
        })
        .catch(error => {
            console.error("Erro ao buscar dados:", error);
        });
}


function getFiltersForTable(tableName) {
    const filters = {};
    document.querySelectorAll(`#${tableName}-filters input`).forEach(input => {
        filters[input.name] = input.value;
    });
    return filters;
}

document.addEventListener("DOMContentLoaded", function() {
    // Listener para botões de tabela.
    const tableButtons = document.querySelectorAll(".btn[data-table-name]");
    tableButtons.forEach(button => {
        button.addEventListener("click", function(e) {
            const tableName = e.target.getAttribute("data-table-name");
            if (tableName) {
                showTableWithFilters(tableName);
            }
        });
    });

    // Listener para botões de filtragem.
    const filterButtons = document.querySelectorAll(".filters .btn");
    filterButtons.forEach(button => {
        button.addEventListener("click", function() {
            const tableName = button.closest(".filters").id.split("-")[0];
            applyFiltersAndFetchData(tableName);
        });
    });

    // Listener para botões de exportação (esse é o novo código).
    const exportButtons = document.querySelectorAll(".print-btn");
    exportButtons.forEach(button => {
        button.addEventListener("click", function() {
            const currentTable = document.querySelector(".table-view > div:not([style*='display: none'])");
            if (currentTable) {
                const tableName = currentTable.id.split("-")[0];
                const filters = getFiltersForTable(tableName);
                fetch(`/export_csv/${tableName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(filters)
                })
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `${tableName}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                })
                .catch(error => console.error("Erro ao exportar CSV:", error));
            }
        });
    });
});