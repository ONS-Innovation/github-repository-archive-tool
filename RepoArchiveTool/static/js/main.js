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