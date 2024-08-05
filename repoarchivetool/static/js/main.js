function insertNoResults(table){
    // Inserts a no results message into the table

    messageRow = table.insertRow(2);
    messageRow.id = "noResults";
    messageRow.classList.add("ons-table__row");
    
    messageCell = messageRow.insertCell(0);
    messageCell.innerHTML = "No results.";
    messageCell.classList.add("ons-table__cell");
    messageCell.colSpan = "8";
    messageCell.style.textAlign = "center";
}

function deleteNoResults(table){
    // Deletes the no results message from the table if it exists

    messageRow = document.getElementById("noResults");
    
    if(messageRow != null){
        rowIndex = messageRow.rowIndex;
        table.deleteRow(rowIndex);
    }
}


function searchRepos(){
    // Searches contents of the repo table in /manage_repositories based on the search inputs

    repoName = document.getElementById("repoSearch").value.toUpperCase();
    repoType = document.getElementById("typeSearch").value.toUpperCase();
    contributorInput = document.getElementById("contribSearch").value.toUpperCase();

    table = document.getElementById("repoTable");

    rows = table.tBodies[0].getElementsByTagName("tr");

    // Try to delete the no results message if it exists
    deleteNoResults(table);

    // If all search inputs are empty, show all rows
    if(repoName == "" && repoType == "" && contributorInput == ""){
        for(i = 0; i < rows.length; i++){
            rows[i].style.display = "";
        }
    }
    else{
        rowsShown = 0;

        for(i = 0; i < rows.length; i++){
    
            // Get the data from the row
            rowContents = rows[i].getElementsByTagName("td");
        
            // Hide the row by default
            rows[i].style.display = "none";
    
            rowRepoName = rowContents[0].innerHTML.toUpperCase();
            rowRepoType = rowContents[1].innerHTML.toUpperCase();
    
            rowContributors = rowContents[2].children;

            // Search for repo name and type
            // If the repo name or type is found, show the row
            if((rowRepoName.indexOf(repoName) > -1 | repoName == "") && (rowRepoType.indexOf(repoType) > -1 | repoType == "")){
                rows[i].style.display = "";
                rowsShown++;
            }

            // if only searching for contributors, rehide row and decrement counter
            if(repoName == "" && repoType == "" && contributorInput != ""){
                rows[i].style.display = "none";
                rowsShown--;
            }
    
            // Search for contributors
            if(contributorInput != ""){
                contributorExists = false;
        
                for(contributor of rowContributors){
                    contributorName = contributor.ariaLabel.toUpperCase();
        
                    // If the contributor is found, highlight the avatar
                    // If not, try and remove the highlight
                    if(contributorName.indexOf(contributorInput) > -1){
                        contributor.children[0].classList.add("highlight");
                        contributorExists = true;
                    }
                    else {
                        if(contributor.children[0].classList.contains("highlight")){
                            contributor.children[0].classList.remove("highlight");
                        }
                    }
                }
    
                // If search has been made for repo name or type, hide rows where the contributor doesn't exist
                if (repoName != "" | repoType != ""){
                    if(!contributorExists && contributorInput != ""){
                        rows[i].style.display = "none";
                    }
                }
                else {
                    // If only searching on contributors, show the row if the contributor exists
                    if(contributorExists | contributorInput == ""){
                        rows[i].style.display = "";
                        rowsShown++;
                    }
                }
            }
            // If no search has been made for contributors, remove any highlights
            else {
                for(contributor of rowContributors){
                    if(contributor.children[0].classList.contains("highlight")){
                        contributor.children[0].classList.remove("highlight");
                    }
                }
            }
        }

        // If no rows are shown, insert a no results message
        if(rowsShown == 0){
            insertNoResults(table);
        }
        else {
            deleteNoResults(table);
        }
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
    // Toggles the visibility of reverted batches in /recently_archived
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