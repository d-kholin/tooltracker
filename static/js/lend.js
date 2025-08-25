
const searchInput = document.getElementById('person-search');
const results = document.getElementById('person-results');
const resultsList = document.getElementById('results-list');
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
    resultsList.innerHTML = '';
    personId.value = '';
    
    if (!term) {
      results.classList.add('hidden');
      return;
    }
    
    const matches = people.filter(p => p.name.toLowerCase().includes(term));
    
    if (matches.length > 0) {
      matches.forEach(p => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-brand focus:ring-inset';
        btn.textContent = p.name;
        btn.dataset.id = p.id;
        resultsList.appendChild(btn);
      });
      results.classList.remove('hidden');
    } else {
      results.classList.add('hidden');
    }
  });

  results.addEventListener('click', (e) => {
    const id = e.target.dataset.id;
    if (!id) return;
    
    personId.value = id;
    searchInput.value = e.target.textContent;
    results.classList.add('hidden');
    
    // Visual feedback
    searchInput.classList.add('border-green-500', 'bg-green-50');
    setTimeout(() => {
      searchInput.classList.remove('border-green-500', 'bg-green-50');
    }, 2000);
  });
}

// Inline add person form
if (showAdd) {
  showAdd.addEventListener('click', () => {
    addForm.classList.toggle('hidden');
    if (!addForm.classList.contains('hidden')) {
      addName.focus();
    }
  });

  addSubmit.addEventListener('click', async () => {
    const name = addName.value.trim();
    if (!name) {
      addName.classList.add('border-red-500');
      addName.focus();
      return;
    }
    
    addName.classList.remove('border-red-500');
    
    try {
      addSubmit.disabled = true;
      addSubmit.innerHTML = `
        <svg class="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Saving...
      `;
      
      const response = await fetch('/people', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ 
          name: name, 
          contact_info: addContact.value.trim() 
        })
      });
      
      if (response.ok) {
        // Success feedback
        addForm.classList.add('hidden');
        addName.value = '';
        addContact.value = '';
        
        // Show success message
        const successMsg = document.createElement('div');
        successMsg.className = 'mt-3 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800 text-sm';
        successMsg.innerHTML = `
          <div class="flex items-center">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            Person added successfully! You can now select them from the search above.
          </div>
        `;
        addForm.appendChild(successMsg);
        
        // Remove success message after 5 seconds
        setTimeout(() => {
          if (successMsg.parentNode) {
            successMsg.remove();
          }
        }, 5000);
        
        // Refresh people data
        window.location.reload();
      } else {
        throw new Error('Failed to add person');
      }
    } catch (error) {
      console.error('Error adding person:', error);
      addSubmit.innerHTML = `
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        Save Person
      `;
      
      // Show error message
      const errorMsg = document.createElement('div');
      errorMsg.className = 'mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm';
      errorMsg.innerHTML = `
        <div class="flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Failed to add person. Please try again.
        </div>
      `;
      addForm.appendChild(errorMsg);
      
      // Remove error message after 5 seconds
      setTimeout(() => {
        if (errorMsg.parentNode) {
          errorMsg.remove();
        }
      }, 5000);
    } finally {
      addSubmit.disabled = false;
    }
  });
}

// Ensure a person is chosen before submitting
if (form && personId) {
  form.addEventListener('submit', (e) => {
    if (!personId.value) {
      e.preventDefault();
      searchInput.focus();
      searchInput.classList.add('border-red-500');
      searchInput.classList.remove('border-gray-300');
      
      // Show error message
      const errorMsg = document.createElement('div');
      errorMsg.className = 'mt-2 text-sm text-red-600';
      errorMsg.textContent = 'Please select a person to lend the tool to.';
      
      const existingError = searchInput.parentNode.querySelector('.text-red-600');
      if (!existingError) {
        searchInput.parentNode.appendChild(errorMsg);
      }
      
      setTimeout(() => {
        searchInput.classList.remove('border-red-500');
        searchInput.classList.add('border-gray-300');
        if (errorMsg.parentNode) {
          errorMsg.remove();
        }
      }, 3000);
    }
  });
}

// Clear error styling when user starts typing
if (searchInput) {
  searchInput.addEventListener('input', () => {
    searchInput.classList.remove('border-red-500');
    searchInput.classList.add('border-gray-300');
    
    const errorMsg = searchInput.parentNode.querySelector('.text-red-600');
    if (errorMsg) {
      errorMsg.remove();
    }
  });
}