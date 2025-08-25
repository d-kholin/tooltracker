export default function TaskCard({ task, onEdit, onDelete }) {
  return (
    <div className="flex justify-between items-center bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition">
      <div>
        <p className="font-medium">{task.name}</p>
        {task.due && (
          <span className="text-xs text-[#1565C0] bg-blue-50 rounded-md px-2 py-0.5">
            {task.dueLabel}
          </span>
        )}
      </div>
      <div className="flex gap-2">
        <button onClick={() => onEdit(task)} className="text-sm text-slate-500">
          Edit
        </button>
        <button onClick={() => onDelete(task)} className="text-sm text-red-500">
          Delete
        </button>
      </div>
    </div>
  );
}
