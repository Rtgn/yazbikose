window.addEventListener("scroll", function() {
    let menu_container = document.getElementById("container");
    let logo_scrooled = document.getElementById("logo");
    let menu_items = document.getElementById("menu");
    let log_items = document.getElementById("log-in-out");
    let drop_down_menu = document.getElementById("dropdown-menu");
    

    if (window.scrollY > 50) {
        menu_container.classList.add("scrolled_mc");
        logo_scrooled.classList.add("scrolled_ls");
        menu_items.classList.add("scrolled_mi");
        log_items.classList.add("scrolled_lio");
        drop_down_menu.classList.add("scrolled_dm");


    } else {
        menu.classList.remove('scrolled_mc');
        logo_scrooled.classList.remove("scrolled_ls");
        menu_items.classList.remove("scrolled_mi");
        log_items.classList.remove("scrolled_lio");
        drop_down_menu.classList.remove("scrolled_dm");
    }
});




