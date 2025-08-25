
const searchInput = document.getElementById('person-search');
const results = document.getElementById('person-results');
const personId = document.getElementById('person-id');
const showAdd = document.getElementById('show-add-person');
const addForm = document.getElementById('add-person-form');
const addName = document.getElementById('new-person-name');
const addContact = document.getElementById('new-person-contact');
const addSubmit = document.getElementById('add-person-submit');
const form = document.querySelector('form');
const people = window.peopleData || [];

// Search and select existing people
if (searchInput) {
  searchInput.addEventListener('input', () => {
    const term = searchInput.value.toLowerCase();
    results.innerHTML = '';
    personId.value = '';
    if (!term) {
      results.classList.add('d-none');
      return;
    }
    const matches = people.filter(p => p.name.toLowerCase().includes(term));
    matches.forEach(p => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'list-group-item list-group-item-action';
      btn.textContent = p.name;
      btn.dataset.id = p.id;
      results.appendChild(btn);
    });
    results.classList.toggle('d-none', matches.length === 0);
  });

  results.addEventListener('click', (e) => {
    const id = e.target.dataset.id;
    if (!id) return;
    personId.value = id;
    searchInput.value = e.target.textContent;
    results.classList.add('d-none');
  });
}

// Inline add person form
if (showAdd) {
  showAdd.addEventListener('click', () => {
    addForm.classList.toggle('d-none');
  });

  addSubmit.addEventListener('click', () => {
    const name = addName.value.trim();
    if (!name) {
      return;
    }
    fetch('/people', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ name: name, contact_info: addContact.value })
    }).then(() => {
      window.location.reload();
    });
  });
}

// Ensure a person is chosen before submitting
if (form && personId) {
  form.addEventListener('submit', (e) => {
    if (!personId.value) {
      e.preventDefault();
      searchInput.focus();
    }
  });
}