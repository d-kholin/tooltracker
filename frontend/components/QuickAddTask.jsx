import { useState } from "react";

export default function QuickAddTask({ onAdd }) {
  const [title, setTitle] = useState("");

  const submit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    onAdd(title.trim());
    setTitle("");
  };

  return (
    <form
      onSubmit={submit}
      className="flex items-center gap-2 bg-white rounded-lg shadow px-3 py-2"
    >
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Add task..."
        className="flex-1 border-none focus:ring-0 font-inter text-sm"
        autoFocus
      />
      <button
        type="submit"
        className="bg-[#1565C0] text-white rounded-md px-4 py-1.5 hover:bg-[#0e4b8f] active:scale-95 transition"
      >
        Add
      </button>
    </form>
  );
}
