// base.html js.
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

// Events include filter js.
const semanticBtn = document.getElementById('semantic-btn');
if (semanticBtn) {
    semanticBtn.addEventListener('click', function() {
        const q = document.querySelector('[name=search]').value.trim();
        const url = semanticBtn.dataset.url + (q ? "?q=" + encodeURIComponent(q) : "");
        window.location.href = url;
    });
}

