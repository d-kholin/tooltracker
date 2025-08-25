const QuickAddTool = ({ onAdd }) => {
  const [name, setName] = React.useState("");

  const submit = e => {
    e.preventDefault();
    if (!name.trim()) return;
    onAdd(name.trim());
    setName("");
  };

  return (
    <form onSubmit={submit} className="flex items-center gap-2 bg-white rounded-lg shadow px-3 py-2">
      <input
        type="text"
        value={name}
        onChange={e => setName(e.target.value)}
        placeholder="Add tool..."
        className="flex-1 border-none focus:ring-0 text-sm"
      />
      <button
        type="submit"
        className="bg-brand text-white rounded-md px-4 py-1.5 hover:bg-blue-700 active:scale-95 transition"
      >
        Add
      </button>
    </form>
  );
};

const ToolCard = ({ tool }) => {
  const navigateToEdit = () => {
    window.location = `/edit/${tool.id}`;
  };
  return (
    <div
      onClick={navigateToEdit}
      className="bg-white rounded-xl p-4 shadow-sm flex justify-between items-center hover:shadow-md transition cursor-pointer"
    >
      <div>
        <p className="font-medium">{tool.name}</p>
        <p className="text-xs text-gray-500">
          {tool.borrower ? `Lent to ${tool.borrower}` : 'Available'}
        </p>
      </div>
      {tool.borrower ? (
        <form
          method="POST"
          action={`/return/${tool.id}`}
          onClick={e => e.stopPropagation()}
        >
          <button type="submit" className="text-sm text-red-500">
            Return
          </button>
        </form>
      ) : (
        <a
          href={`/lend/${tool.id}`}
          className="text-sm text-brand"
          onClick={e => e.stopPropagation()}
        >
          Lend
        </a>
      )}
    </div>
  );
};

const BottomNav = ({ current }) => {
  const items = [
    { id: 'tools', label: 'Tools', href: '/' },
    { id: 'add', label: '+', href: '/add' },
    { id: 'people', label: 'People', href: '/people' }
  ];
  return (
    <nav className="fixed bottom-0 inset-x-0 bg-white border-t flex justify-around py-2 shadow">
      {items.map(item => (
        <a key={item.id} href={item.href} className={current===item.id ? 'text-brand' : 'text-gray-400'}>
          {item.label}
        </a>
      ))}
    </nav>
  );
};

const App = () => {
  const [tools, setTools] = React.useState([]);

  React.useEffect(() => {
    fetch('/api/tools')
      .then(res => res.json())
      .then(data => setTools(data));
  }, []);

  const addTool = async name => {
    const res = await fetch('/api/tools', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    if (res.ok) {
      const tool = await res.json();
      setTools([...tools, tool]);
    }
  };

  return (
    <div className="pb-20 space-y-4">
      <QuickAddTool onAdd={addTool} />
      <div className="space-y-3">
        {tools.map(tool => (
          <ToolCard key={tool.id} tool={tool} />
        ))}
      </div>
      <BottomNav current="tools" />
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
