document.addEventListener("DOMContentLoaded", () => {
    const searchBar = document.getElementById('search-bar');
    const searchInput = document.querySelector('.search-bar input');
    const filters = document.getElementById('filters-block');
    const actions = document.getElementById('form-actions');
    const form = document.getElementById('search-form');

    if (searchInput) {
        searchInput.addEventListener('focus', () => {
            filters.style.display = "block";
            actions.style.display = "flex";
            searchBar.style.marginBottom = '15px';
        });
    }

    document.addEventListener('click', (e) => {
        if (!form) return;
        if (!form.contains(e.target)) {
            filters.style.display = "none";
            actions.style.display = "none";
            searchBar.style.marginBottom = '0px';
        }
    });
});