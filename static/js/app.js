const App = () => {
  const [tools, setTools] = React.useState([]);

  React.useEffect(() => {
    fetch('/api/tools')
      .then(res => res.json())
      .then(data => setTools(data));
  }, []);

  return (
    <div className="container">
      <h1 className="mb-4">Tools</h1>
      <div className="row row-cols-1 row-cols-md-3 g-4">
        {tools.map(tool => (
          <div className="col" key={tool.id}>
            <div
              className="card h-100"
              onClick={() => (window.location.href = `/edit/${tool.id}`)}
              style={{ cursor: 'pointer' }}
            >
              {tool.image_path && (
                <img src={`/static/${tool.image_path}`} className="card-img-top" alt={tool.name} />
              )}
              <div className="card-body">
                <h5 className="card-title">
                  <a href={`/edit/${tool.id}`} className="text-decoration-none" onClick={e => e.stopPropagation()}>
                    {tool.name}
                  </a>
                </h5>
                {tool.value !== null && (
                  <p className="card-text">${tool.value.toFixed(2)}</p>
                )}
                <p className="card-text">
                  <small className="text-muted">
                    {tool.borrower ? `Lent to ${tool.borrower} on ${tool.lent_on}` : 'Available'}
                  </small>
                </p>
                <div className="d-flex gap-2">
                  <a
                    href={`/edit/${tool.id}`}
                    className="btn btn-sm btn-secondary"
                    onClick={e => e.stopPropagation()}
                  >
                    Edit
                  </a>
                  {tool.borrower ? (
                    <form
                      method="post"
                      action={`/return/${tool.id}`}
                      className="m-0"
                      onClick={e => e.stopPropagation()}
                    >
                      <button type="submit" className="btn btn-sm btn-warning">Return</button>
                    </form>
                  ) : (
                    <a
                      href={`/lend/${tool.id}`}
                      className="btn btn-sm btn-primary"
                      onClick={e => e.stopPropagation()}
                    >
                      Lend
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
