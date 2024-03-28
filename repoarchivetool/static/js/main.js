// Event listener to change navbar when screen resizes
window.addEventListener('resize', () => {
    movePATForm();

    
});

// Moves the PAT token form between the navbar and inputBar
function movePATForm(){
    screenWidth = window.innerWidth;
    tokenInput = document.getElementById("tokenInput");
    themeSwitch = document.getElementById("themeSwitch");
    inputBar = document.getElementById("inputBar");
    navbar = document.getElementById("navbar");

    // Get a navInput's parent's id to check if it's in the navbar or inputBar
    parentID = tokenInput.parentElement.id;

    if(screenWidth <= 990 && parentID == "navbar"){
        inputBar.appendChild(tokenInput);
        inputBar.hidden = false;
    }
    
    if(screenWidth > 990 && parentID == "inputBar"){
        navbar.insertBefore(tokenInput, themeSwitch);
        inputBar.hidden = true;
    }
}

// Loads theme from sessionStorage
function loadTheme(){
    if(sessionStorage.theme == "dark"){
        document.documentElement.setAttribute("data-bs-theme", "dark");
        document.getElementById("themeIcon").className = "fa fa-moon-o";
    }
    else {
        document.documentElement.setAttribute("data-bs-theme", "light");
        document.getElementById("themeIcon").className = "fa fa-sun-o";
    }
}

// Switches the theme based on the navbar checkbox
function toggleTheme(){
    // Get current theme
    theme = document.documentElement.getAttribute("data-bs-theme");

    if(theme == "dark"){
        // Change theme and apply to Session Storage if supported
        document.documentElement.setAttribute("data-bs-theme", "light");
        sessionStorage.theme = "light";

        // Change theme icon
        document.getElementById("themeIcon").className = "fa fa-sun-o";
    }
    else {
        document.documentElement.setAttribute("data-bs-theme", "dark");
        sessionStorage.theme = "dark";

        // Change theme icon
        document.getElementById("themeIcon").className = "fa fa-moon-o";
    }
}