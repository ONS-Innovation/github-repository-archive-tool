function insertNoResults(table){
    messageRow = table.insertRow(1);
    messageRow.id = "noResults";
    messageRow.classList.add("ons-table__row");
    
    messageCell = messageRow.insertCell(0);
    messageCell.innerHTML = "No results.";
    messageCell.classList.add("ons-table__cell");
    messageCell.colSpan = "6";
    messageCell.style.textAlign = "center";
}

function deleteNoResults(table){
    messageRow = document.getElementById("noResults");
    
    if(messageRow != null){
        rowIndex = messageRow.rowIndex;
        table.deleteRow(rowIndex);
    }
}

function searchTable(tableID, searchbarID, columnIndex) {
    searchBar = document.getElementById(searchbarID);
    searchValue = searchBar.value.toUpperCase();
    table = document.getElementById(tableID);
    rows = table.getElementsByTagName("tr");

    // Used to show or hide no results message. Removed 1 from length for heading row.
    noOfResults = rows.length - 1;
    rowsHidden = 0;

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
                rowsHidden++;
            }
        }
    }
    
    if(noOfResults == rowsHidden){
        insertNoResults(table);
    }
    else {
        deleteNoResults(table);
    }
}

function searchContributors(tableID, searchbarID, columnIndex) {
    searchBar = document.getElementById(searchbarID);
    searchValue = searchBar.value.toUpperCase();
    table = document.getElementById(tableID);
    rows = table.getElementsByTagName("tr");

    // Used to show or hide no results message. Removed 1 from length for heading row.
    noOfResults = rows.length - 1;
    rowsHidden = 0;

    // Loop through all table rows, and hide those who don't match the search query
    for(i = 0; i < rows.length; i++){
        rowData = rows[i].getElementsByTagName("td")[columnIndex];

        if(rowData){
            rowChildren = rowData.children;

            found = false;

            for(const child of rowChildren){
                contributorElement = child;
                contributorName = contributorElement.ariaLabel;

                if(contributorName.toUpperCase().indexOf(searchValue) > -1 && searchValue != ""){
                    found = true;

                    // Add a border to the contributor's avatar
                    contributorElement.children[0].classList.add("highlight");
                }
                else {
                    // Remove the border
                    if(contributorElement.children[0].classList.contains("highlight")){
                        contributorElement.children[0].classList.remove("highlight");
                    }
                }
            }      
            
            if(searchValue == ""){
                found = true;
            }

            if(found){
                rows[i].style.display = "";
            }
            else{
                rows[i].style.display = "none";
                rowsHidden++;
            }
        }
    }

    if(noOfResults == rowsHidden){
        insertNoResults(table);
    }
    else {
        deleteNoResults(table);
    }
}

function searchBatches(searchbarID){
    // Searches for a repo within a list of archive batches

    searchBar = document.getElementById(searchbarID);
    searchValue = searchBar.value.toUpperCase();

    noOfRepos = document.getElementsByClassName("ons-card").length;
    reposHidden = 0;

    batches = document.getElementsByClassName("ons-details--accordion");

    for(batch of batches){
        repoCards = batch.getElementsByClassName("ons-card");

        if(repoCards.length == 0){
            if(searchValue != ""){
                batch.style.display = "none";
            }
            else {
                batch.style.display = "";
            }
        }
        else {
            for(card of repoCards){
                if(card.innerText.toUpperCase().indexOf(searchValue) > -1){
                    batch.style.display = "";
                    break;
                }
                else {
                    batch.style.display = "none";
                    reposHidden++;
                }
            }
        }
    }

    document.getElementById("noBatchesMessage").hidden = reposHidden == noOfRepos ? false : true;
}

function toggleRevertedBatches(){
    checkbox = document.getElementById("hideReverted");
    hideReverted = checkbox.checked;

    // Clear any previous search results before showing/hiding reverted batches
    document.getElementById("archiveSearch").value = "";
    searchBatches("archiveSearch");

    batches = document.getElementsByClassName("ons-details--accordion");
        
    if(hideReverted){
        for(batch of batches){
            if(batch.getElementsByClassName("ons-card").length == 0){
                batch.style.display = "none";
            }
        }
    }
    else{
        for(batch of batches){
            batch.style.display = "";
        }
    }
}