const toggleBtn = document.getElementById('toggle-dashboard');
const drawer = document.getElementById('dashboard-drawer');
const closeBtn = document.getElementById('close-dashboard');

toggleBtn.addEventListener('click', () => {
drawer.classList.add('open');
drawer.classList.remove('dashboard-closed');
});

closeBtn.addEventListener('click', () => {
drawer.classList.remove('open');
drawer.classList.add('dashboard-closed');
});

// Optional: close drawer if clicked outside
document.addEventListener('click', function (event) {
if (
    !drawer.contains(event.target) &&
    !toggleBtn.contains(event.target)
) {
    drawer.classList.remove('open');
    drawer.classList.add('dashboard-closed');
}
});
