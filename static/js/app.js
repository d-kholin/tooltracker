const ToolCard = ({ tool }) => {
  const navigateToEdit = () => {
    window.location = `/edit/${tool.id}`;
  };
  
  return (
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200 cursor-pointer group">
      <div class="flex items-start justify-between">
        <div class="flex-1" onClick={navigateToEdit}>
          <div class="flex items-start gap-4 mb-3">
            {tool.image_path ? (
              <div class="flex-shrink-0">
                <img 
                  src={`/static/${tool.image_path}`} 
                  alt={tool.name}
                  class="w-16 h-16 object-cover rounded-lg border border-gray-200 group-hover:border-brand transition-colors"
                />
              </div>
            ) : (
              <div class="w-16 h-16 bg-brand-light rounded-lg flex items-center justify-center group-hover:bg-brand transition-colors flex-shrink-0">
                <svg class="w-8 h-8 text-brand group-hover:text-white transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
              </div>
            )}
            
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 text-lg group-hover:text-brand transition-colors truncate">{tool.name}</h3>
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
        
        <div class="flex flex-col gap-2 ml-4">
          {tool.borrower ? (
            <form
              method="POST"
              action={`/return/${tool.id}`}
              onClick={e => e.stopPropagation()}
            >
              <button type="submit" class="btn btn-sm btn-secondary">
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                Return
              </button>
            </form>
          ) : (
            <a
              href={`/lend/${tool.id}`}
              class="btn btn-sm btn-primary"
              onClick={e => e.stopPropagation()}
            >
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              Lend
            </a>
          )}
          
          <button
            onClick={navigateToEdit}
            class="btn btn-sm btn-secondary"
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Edit
          </button>
        </div>
      </div>
    </div>
  );
};

const EmptyState = () => (
  <div class="text-center py-12">
    <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
      <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
      </svg>
    </div>
    <h3 class="text-lg font-medium text-gray-900 mb-2">No tools yet</h3>
    <p class="text-gray-500 mb-4">Get started by adding your first tool to track.</p>
    <a href="/add" class="btn btn-primary">
      <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
      </svg>
      Add Your First Tool
    </a>
  </div>
);

const App = () => {
  const [tools, setTools] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    fetch('/api/tools')
      .then(res => res.json())
      .then(data => {
        setTools(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          Add Tool
        </a>
      </div>
      
      {tools.length === 0 ? (
        <EmptyState />
      ) : (
        <div class="space-y-4">
          {tools.map(tool => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
        </div>
      )}
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
