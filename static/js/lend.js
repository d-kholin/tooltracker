const select = document.getElementById('person-select');
const searchInput = document.getElementById('person-search');

// Filter people as user types
if (searchInput && select) {
  searchInput.addEventListener('input', () => {
    const term = searchInput.value.toLowerCase();
    Array.from(select.options).forEach(opt => {
      if (!opt.value || opt.value === '__add_new__') return;
      const text = opt.textContent.toLowerCase();
      opt.hidden = !text.includes(term);
    });
  });

  select.addEventListener('change', () => {
    if (select.value === '__add_new__') {
      const name = prompt('Enter name for new person:');
      if (!name) {
        select.value = '';
        return;
      }
      const contact = prompt('Enter contact info (optional):') || '';
      fetch('/people', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ name: name, contact_info: contact })
      }).then(() => {
        window.location.reload();
      });
    }
  });
}
