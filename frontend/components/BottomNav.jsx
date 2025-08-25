import { HomeIcon, PlusIcon, UsersIcon, ClipboardIcon } from "@heroicons/react/24/outline";

export default function BottomNav({ current }) {
  const items = [
    { id: "tools", icon: <HomeIcon className="h-6" /> },
    { id: "tasks", icon: <ClipboardIcon className="h-6" /> },
    {
      id: "add",
      icon: (
        <PlusIcon className="h-8 text-white p-1 bg-[#1565C0] rounded-full -mt-4" />
      ),
    },
    { id: "people", icon: <UsersIcon className="h-6" /> },
  ];

  return (
    <nav className="fixed bottom-0 inset-x-0 bg-white border-t flex justify-around py-2 shadow-md">
      {items.map((item) => (
        <button
          key={item.id}
          aria-label={item.id}
          className={`flex flex-col items-center ${
            current === item.id ? "text-[#1565C0]" : "text-gray-400"
          }`}
        >
          {item.icon}
        </button>
      ))}
    </nav>
  );
}
