function searchTable(tableID, searchbarID, columnIndex) {
    searchBar = document.getElementById(searchbarID);
    searchValue = searchBar.value.toUpperCase();
    table = document.getElementById(tableID);
    rows = table.getElementsByTagName("tr");

    // Loop through all table rows, and hide those who don't match the search query
    for(i = 0; i < rows.length; i++){
        rowData = rows[i].getElementsByTagName("td")[columnIndex];
        if(rowData){
            rowValue = rowData.textContent || rowData.innerText;

            if(rowValue.toUpperCase().indexOf(searchValue) > -1){
                rows[i].style.display = "";
            }
            else{
                rows[i].style.display = "none";
            }
        }
    }
}

function sortTable(tableID, columnIndex){
    console.log("sorting")

    table = document.getElementById(tableID);

    switching = true;

    // Get the table heading of the column being sorted to work out if column should be sorted
    // in asc or desc order
    rows = table.rows;
    columnHeading = rows[0].getElementsByTagName('th')[columnIndex];

    if(columnHeading.classList.contains("asc")){
        sortOrder = "desc";
        columnHeading.classList.remove("asc");
    }
    else{
        sortOrder = "asc";
        columnHeading.classList.remove("desc");
    }

    columnHeading.classList.add(sortOrder);

    while(switching){
        switching = false;

        rows = table.rows;

        for(i=1; i < (rows.length - 1); i++){
            swap = false;

            currentRow = rows[i].getElementsByTagName('TD')[columnIndex];
            nextRow = rows[i + 1].getElementsByTagName('TD')[columnIndex];

            if(sortOrder == "asc"){
                if(currentRow.innerHTML.toLowerCase() > nextRow.innerHTML.toLowerCase()){
                    swap = true;
                    break;
                }
            }
            else{
                if(currentRow.innerHTML.toLowerCase() < nextRow.innerHTML.toLowerCase()){
                    swap = true;
                    break;
                }
            }
        }

        if(swap){
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
}