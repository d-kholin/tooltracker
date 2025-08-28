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
      className="tool-card bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group" 
      onClick={handleCardClick}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-start gap-4 mb-3">
            {tool.image_path ? (
              <div className="flex-shrink-0">
                <img 
                  src={`/data/${tool.image_path}`} 
                  alt={tool.name}
                  className="w-16 h-16 object-cover rounded-lg border border-gray-200 group-hover:border-brand transition-colors"
                />
                {/* Show badge below image on mobile only */}
                <div className="md:hidden mt-2">
                  <BrandBadge brand={tool.brand} />
                </div>
              </div>
            ) : (
              <div className="flex-shrink-0">
                <div className="w-16 h-16 bg-brand-light rounded-lg flex items-center justify-center group-hover:bg-brand transition-colors">
                  <svg className="w-8 h-8 text-brand group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                  </svg>
                </div>
                {/* Show badge below placeholder on mobile only */}
                <div className="md:hidden mt-2">
                  <BrandBadge brand={tool.brand} />
                </div>
              </div>
            )}
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                {/* Show brand badge before tool name on desktop only */}
                <div className="hidden md:block">
                  <BrandBadge brand={tool.brand} />
                </div>
                <h3 className="font-semibold text-gray-900 text-lg group-hover:text-brand transition-colors truncate">{tool.name}</h3>
              </div>
              <div className="flex items-center gap-2 mt-1">
                {tool.borrower ? (
                  <span className="status-lent">Lent to {tool.borrower}</span>
                ) : (
                  <span className="status-available">Available</span>
                )}
              </div>
              

            </div>
          </div>
        </div>
        
        {/* Desktop action buttons - hidden on mobile */}
        <div className="action-buttons hidden md:flex flex-col gap-2 ml-4">
          {tool.borrower ? (
            <form
              method="POST"
              action={`/return/${tool.id}`}
              onClick={handleReturnClick}
              data-action="return"
            >
              <button type="submit" className="btn btn-sm btn-secondary" data-action="return">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Return
              </button>
            </form>
          ) : (
            <a
              href={`/lend/${tool.id}`}
              className="btn btn-sm btn-primary"
              onClick={handleLendClick}
              data-action="lend"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Lend
            </a>
          )}
          
          <button
            onClick={handleEditClick}
            className="btn btn-sm btn-secondary"
            data-action="edit"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
          </button>
          
          <button
            onClick={handleHistoryClick}
            className="btn btn-sm btn-secondary"
            data-action="history"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            History
          </button>
        </div>
      </div>
      
      {/* Mobile action buttons - horizontal layout at bottom */}
      <div className="md:hidden mt-4 pt-4 border-t border-gray-100">
        <div className="flex gap-2 justify-start">
          {tool.borrower ? (
            <form
              method="POST"
              action={`/return/${tool.id}`}
              onClick={handleReturnClick}
              data-action="return"
              className="flex-1"
            >
              <button type="submit" className="btn btn-sm btn-secondary w-full" data-action="return">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Return
              </button>
            </form>
          ) : (
            <a
              href={`/lend/${tool.id}`}
              className="btn btn-sm btn-primary flex-1 text-center"
              onClick={handleLendClick}
              data-action="lend"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Lend
            </a>
          )}
          
          <button
            onClick={handleEditClick}
            className="btn btn-sm btn-secondary flex-1"
            data-action="edit"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
          </button>
          
          <button
            onClick={handleHistoryClick}
            className="btn btn-sm btn-secondary flex-1"
            data-action="history"
          >
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
  <div className="relative">
    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
      </svg>
    </div>
    <input
      type="text"
              placeholder="Search tools by name, description, brand, model, serial number, or borrower..."
      value={searchTerm}
      onChange={(e) => onSearchChange(e.target.value)}
      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-brand focus:border-brand sm:text-sm"
    />
  </div>
);

const BrandFilter = ({ brands, selectedBrand, onBrandChange }) => (
  <div className="relative">
    <select
      value={selectedBrand}
      onChange={(e) => onBrandChange(e.target.value)}
      className="block w-full px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white text-gray-900 focus:outline-none focus:ring-1 focus:ring-brand focus:border-brand sm:text-sm"
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
      <span className="inline-flex items-center justify-center px-2 py-1 rounded-lg text-xs font-medium bg-white border border-gray-200 shadow-sm w-20 h-8">
        <img 
          src={brandInfo.logo} 
          alt={brand} 
          className="h-6 w-auto max-w-16 object-contain"
          onError={(e) => {
            // Fallback to text if logo fails to load
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'inline';
          }}
        />
        <span className="hidden text-gray-700">{brand}</span>
      </span>
    );
  } else {
    // Fallback to colored text badge
    const colors = (brandInfo && brandInfo.fallback) || { bg: 'bg-gray-500', text: 'text-white', border: 'border-gray-600' };
    
    return (
      <span className={`inline-flex items-center justify-center px-2 py-1 rounded-full text-xs font-medium ${colors.bg} ${colors.text} ${colors.border} border w-20 h-8`}>
        {brand}
      </span>
    );
  }
};

const EmptyState = ({ isSearching }) => (
  <div className="text-center py-12">
    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
      {isSearching ? (
        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
      ) : (
        <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
      )}
    </div>
    <h3 className="text-lg font-medium text-gray-900 mb-2">
      {isSearching ? 'No tools found' : 'No tools yet'}
    </h3>
    <p className="text-gray-500 mb-4">
      {isSearching 
        ? 'Try adjusting your search terms or browse all tools.' 
        : 'Get started by adding your first tool to track.'
      }
    </p>
    {!isSearching && (
      <a href="/add" className="btn btn-primary">
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
  const [loadingMore, setLoadingMore] = React.useState(false);
  const [filtering, setFiltering] = React.useState(false);
  const [error, setError] = React.useState(null);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = React.useState('');
  const [brands, setBrands] = React.useState([]);
  const [selectedBrand, setSelectedBrand] = React.useState('');
  const [pagination, setPagination] = React.useState({
    page: 1,
    per_page: 20,
    total_count: 0,
    total_pages: 0,
    has_next: false,
    has_prev: false
  });

  // Function to fetch tools with current filters
  const fetchTools = React.useCallback(async (page = 1, append = false) => {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: '20'
    });
    
    if (debouncedSearchTerm.trim()) {
      params.append('search', debouncedSearchTerm.trim());
    }
    
    if (selectedBrand) {
      params.append('brand', selectedBrand);
    }

    try {
      const response = await fetch(`/api/tools?${params}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      
      if (append) {
        setTools(prevTools => [...prevTools, ...data.tools]);
      } else {
        setTools(data.tools);
      }
      
      setPagination(data.pagination);
      setError(null);
    } catch (error) {
      console.error('Error fetching tools:', error);
      setError('Failed to load tools. Please try again.');
      if (!append) {
        setTools([]);
      }
    }
  }, [debouncedSearchTerm, selectedBrand]);

  // Initial load
  React.useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Fetch brands first
        const brandsResponse = await fetch('/api/brands');
        if (!brandsResponse.ok) {
          throw new Error(`HTTP error! status: ${brandsResponse.status}`);
        }
        const brandsData = await brandsResponse.json();
        setBrands(brandsData);
        
        // Then fetch first page of tools
        await fetchTools(1, false);
        setLoading(false);
      } catch (error) {
        console.error('Error loading initial data:', error);
        setError('Failed to load initial data. Please refresh the page.');
        setLoading(false);
      }
    };
    
    loadInitialData();
  }, []);

  // Debounce search term to avoid excessive API calls
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300); // 300ms delay

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Load more tools when filters change
  React.useEffect(() => {
    if (!loading) {
      // Reset pagination when filters change
      setPagination(prev => ({ ...prev, page: 1 }));
      setFiltering(true);
      fetchTools(1, false).finally(() => setFiltering(false));
    }
  }, [debouncedSearchTerm, selectedBrand, fetchTools]);

  // Infinite scroll handler with throttling
  const handleScroll = React.useCallback(() => {
    if (loadingMore || !pagination.has_next) return;
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    // Load more when user is near bottom (within 100px)
    if (scrollTop + windowHeight >= documentHeight - 100) {
      // Throttle scroll events to avoid excessive API calls
      if (!handleScroll.throttled) {
        handleScroll.throttled = true;
        setTimeout(() => {
          handleScroll.throttled = false;
        }, 100);
        loadMoreTools();
      }
    }
  }, [loadingMore, pagination.has_next]);

  // Load more tools
  const loadMoreTools = async () => {
    if (loadingMore || !pagination.has_next) return;
    
    setLoadingMore(true);
    const nextPage = pagination.page + 1;
    await fetchTools(nextPage, true);
    setLoadingMore(false);
  };

  // Add scroll listener
  React.useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tools</h1>
          <p className="text-gray-600 mt-1">Manage and track your tools and equipment</p>
        </div>
        <a href="/add" className="btn btn-primary">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Add Tool
        </a>
      </div>
      
      {/* Search Bar and Brand Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <SearchBar 
            searchTerm={searchTerm} 
            onSearchChange={setSearchTerm} 
          />
        </div>
        <div className="w-full sm:w-48">
          <BrandFilter 
            brands={brands} 
            selectedBrand={selectedBrand} 
            onBrandChange={setSelectedBrand} 
          />
        </div>
      </div>
      
      {/* Results count and filtering indicator */}
      {(debouncedSearchTerm || selectedBrand) && (
        <div className="text-sm text-gray-600">
          Found {pagination.total_count} tool{pagination.total_count !== 1 ? 's' : ''}
          {debouncedSearchTerm && ` matching "${debouncedSearchTerm}"`}
          {selectedBrand && ` from ${selectedBrand}`}
          {pagination.total_pages > 1 && ` (showing ${tools.length} of ${pagination.total_count})`}
        </div>
      )}
      
      {/* Error display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span className="text-red-800">{error}</span>
            <button 
              onClick={() => fetchTools(1, false)} 
              className="ml-auto text-red-600 hover:text-red-800 underline text-sm"
            >
              Retry
            </button>
          </div>
        </div>
      )}
      
      {/* Filtering indicator */}
      {filtering && (
        <div className="flex items-center justify-center py-4 text-gray-600">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-brand mr-2"></div>
          <span>Applying filters...</span>
        </div>
      )}
      
      {tools.length === 0 && !error ? (
        <EmptyState isSearching={!!debouncedSearchTerm} isFiltering={!!selectedBrand} />
      ) : (
        <div className="space-y-4">
          {tools.map(tool => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
          
          {/* Loading more indicator */}
          {loadingMore && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand"></div>
              <span className="ml-3 text-gray-600">Loading more tools...</span>
            </div>
          )}
          
          {/* Load More button (alternative to infinite scroll) */}
          {pagination.has_next && !loadingMore && (
            <div className="text-center py-6">
              <button
                onClick={loadMoreTools}
                className="btn btn-secondary px-8 py-3"
                disabled={loadingMore}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
                </svg>
                Load More Tools
                <span className="ml-2 text-sm text-gray-500">
                  ({pagination.total_count - tools.length} remaining)
                </span>
              </button>
            </div>
          )}
          
          {/* End of results indicator */}
          {!pagination.has_next && tools.length > 0 && (
            <div className="text-center py-8 text-gray-500 border-t border-gray-100">
              <p>You've reached the end of your tool library</p>
              {pagination.total_count > 0 && (
                <p className="text-sm mt-1">Showing all {pagination.total_count} tools</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
