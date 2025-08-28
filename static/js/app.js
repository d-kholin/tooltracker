const ToolCard = ({ tool }) => {
  const navigateToDetail = () => {
    window.location.href = `/tool/${tool.id}`;
  };
  
  const navigateToEdit = (e) => {
    e.preventDefault();
    e.stopPropagation();
    window.location.href = `/edit/${tool.id}`;
  };
  
  const handleLendClick = (e) => {
    e.stopPropagation();
    // Don't prevent default - let the link navigate naturally
  };
  
  const handleReturnClick = (e) => {
    e.stopPropagation();
    // Don't prevent default - let the form submit naturally
  };
  
  const handleEditClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    navigateToEdit(e);
  };
  
  const handleHistoryClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    navigateToDetail();
  };
  
  const handleCardClick = (e) => {
    // Check if we clicked on an action element - be more specific
    const target = e.target;
    
    // Check if the target OR any of its ancestors is an action element
    const isActionElement = target.closest('[data-action]') || 
                           target.closest('button') || 
                           target.closest('form') || 
                           target.closest('a') ||
                           target.closest('input') ||
                           target.closest('select') ||
                           target.closest('textarea');
    
    if (!isActionElement) {
      navigateToDetail();
    }
  };
  
  return (
    <div 
      class="tool-card bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group" 
      onClick={handleCardClick}
    >
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <div class="flex items-start gap-4 mb-3">
            {tool.image_path ? (
              <div class="flex-shrink-0">
                <img 
                  src={`/data/${tool.image_path}`} 
                  alt={tool.name}
                  class="w-16 h-16 object-cover rounded-lg border border-gray-200 group-hover:border-brand transition-colors"
                />
              </div>
            ) : (
              <div class="w-16 h-16 bg-brand-light rounded-lg flex items-center justify-center group-hover:bg-brand transition-colors flex-shrink-0">
                <svg class="w-8 h-8 text-brand group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
              </div>
            )}
            
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-semibold text-gray-900 text-lg group-hover:text-brand transition-colors truncate">{tool.name}</h3>
                <BrandBadge brand={tool.brand} />
              </div>
              <div class="flex items-center gap-2 mt-1">
                {tool.borrower ? (
                  <span class="status-lent">Lent to {tool.borrower}</span>
                ) : (
                  <span class="status-available">Available</span>
                )}
              </div>
              
              {tool.description && (
                <p class="text-gray-600 text-sm mt-2 line-clamp-2">{tool.description}</p>
              )}
              
              {tool.value && (
                <p class="text-sm text-gray-500 mt-1">Value: ${tool.value}</p>
              )}
            </div>
          </div>
        </div>
        
        <div class="action-buttons flex flex-col gap-2 ml-4">
          {tool.borrower ? (
            <form
              method="POST"
              action={`/return/${tool.id}`}
              onClick={handleReturnClick}
              data-action="return"
            >
              <button type="submit" class="btn btn-sm btn-secondary" data-action="return">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Return
              </button>
            </form>
          ) : (
            <a
              href={`/lend/${tool.id}`}
              class="btn btn-sm btn-primary"
              onClick={handleLendClick}
              data-action="lend"
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Lend
            </a>
          )}
          
          <button
            onClick={handleEditClick}
            class="btn btn-sm btn-secondary"
            data-action="edit"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
          </button>
          
          <button
            onClick={handleHistoryClick}
            class="btn btn-sm btn-secondary"
            data-action="history"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            History
          </button>
        </div>
      </div>
    </div>
  );
};

const SearchBar = ({ searchTerm, onSearchChange }) => (
  <div class="relative">
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
      </svg>
    </div>
    <input
      type="text"
              placeholder="Search tools by name, description, brand, model, serial number, or borrower..."
      value={searchTerm}
      onChange={(e) => onSearchChange(e.target.value)}
      class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-brand focus:border-brand sm:text-sm"
    />
  </div>
);

const BrandFilter = ({ brands, selectedBrand, onBrandChange }) => (
  <div class="relative">
    <select
      value={selectedBrand}
      onChange={(e) => onBrandChange(e.target.value)}
      class="block w-full px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white text-gray-900 focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand sm:text-sm"
    >
      <option value="">All Brands</option>
      {brands.map(brand => (
        <option key={brand} value={brand}>{brand}</option>
      ))}
    </select>
  </div>
);

const BrandBadge = ({ brand }) => {
  if (!brand) return null;
  
  // Get brand info from the brand-logos.js file
  const brandInfo = getBrandInfo(brand);
  
  if (brandInfo && brandInfo.logo) {
    // Show logo badge
    return (
      <span class="inline-flex items-center px-2 py-1 rounded-lg text-xs font-medium bg-white border border-gray-200 shadow-sm">
        <img 
          src={brandInfo.logo} 
          alt={brand} 
          class="h-4 w-auto max-w-16 object-contain"
          onError={(e) => {
            // Fallback to text if logo fails to load
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'inline';
          }}
        />
        <span class="hidden text-gray-700">{brand}</span>
      </span>
    );
  } else {
    // Fallback to colored text badge
    const colors = (brandInfo && brandInfo.fallback) || { bg: 'bg-gray-500', text: 'text-white', border: 'border-gray-600' };
    
    return (
      <span class={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text} ${colors.border} border`}>
        {brand}
      </span>
    );
  }
};

const EmptyState = ({ isSearching }) => (
  <div class="text-center py-12">
    <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
      {isSearching ? (
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      ) : (
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
      )}
    </div>
    <h3 class="text-lg font-medium text-gray-900 mb-2">
      {isSearching ? 'No tools found' : 'No tools yet'}
    </h3>
    <p class="text-gray-500 mb-4">
      {isSearching 
        ? 'Try adjusting your search terms or browse all tools.' 
        : 'Get started by adding your first tool to track.'
      }
    </p>
    {!isSearching && (
      <a href="/add" class="btn btn-primary">
        <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        Add Your First Tool
      </a>
    )}
  </div>
);

const App = () => {
  const [tools, setTools] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [brands, setBrands] = React.useState([]);
  const [selectedBrand, setSelectedBrand] = React.useState('');

  React.useEffect(() => {
    // Fetch tools and brands in parallel
    Promise.all([
      fetch('/api/tools'),
      fetch('/api/brands')
    ])
      .then(responses => Promise.all(responses.map(res => res.json())))
      .then(([toolsData, brandsData]) => {
        setTools(toolsData);
        setBrands(brandsData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Filter tools based on search term and brand selection
  const filteredTools = tools.filter(tool => {
    // Brand filter
    if (selectedBrand && tool.brand !== selectedBrand) {
      return false;
    }
    
    // Search term filter
    if (!searchTerm.trim()) return true;
    
    const searchLower = searchTerm.toLowerCase();
    return (
      tool.name.toLowerCase().includes(searchLower) ||
      (tool.description && tool.description.toLowerCase().includes(searchLower)) ||
      (tool.brand && tool.brand.toLowerCase().includes(searchLower)) ||
      (tool.model_number && tool.model_number.toLowerCase().includes(searchLower)) ||
      (tool.serial_number && tool.serial_number.toLowerCase().includes(searchLower)) ||
      (tool.borrower && tool.borrower.toLowerCase().includes(searchLower))
    );
  });

  if (loading) {
    return (
      <div class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div>
      </div>
    );
  }

  return (
    <div class="space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Tools</h1>
          <p class="text-gray-600 mt-1">Manage and track your tools and equipment</p>
        </div>
        <a href="/add" class="btn btn-primary">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Add Tool
        </a>
      </div>
      
      {/* Search Bar and Brand Filter */}
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <SearchBar 
            searchTerm={searchTerm} 
            onSearchChange={setSearchTerm} 
          />
        </div>
        <div class="w-full sm:w-48">
          <BrandFilter 
            brands={brands} 
            selectedBrand={selectedBrand} 
            onBrandChange={setSelectedBrand} 
          />
        </div>
      </div>
      
      {/* Results count */}
      {(searchTerm || selectedBrand) && (
        <div class="text-sm text-gray-600">
          Found {filteredTools.length} tool{filteredTools.length !== 1 ? 's' : ''}
          {searchTerm && ` matching "${searchTerm}"`}
          {selectedBrand && ` from ${selectedBrand}`}
        </div>
      )}
      
      {filteredTools.length === 0 ? (
        <EmptyState isSearching={!!searchTerm} isFiltering={!!selectedBrand} />
      ) : (
        <div class="space-y-4">
          {filteredTools.map(tool => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
        </div>
      )}
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
