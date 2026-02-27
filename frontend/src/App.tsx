import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import Sessions from "./pages/Sessions";
import "./style.css";

type Page = "dashboard" | "sessions" | "search" | "analytics" | "tools" | "memory" | "settings";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "sessions":
        return <Sessions />;
      case "search":
        return <div className="p-6"><h1 className="text-3xl font-bold">Search (Coming Soon)</h1></div>;
      case "analytics":
        return <div className="p-6"><h1 className="text-3xl font-bold">Analytics (Coming Soon)</h1></div>;
      case "tools":
        return <div className="p-6"><h1 className="text-3xl font-bold">Tools (Coming Soon)</h1></div>;
      case "memory":
        return <div className="p-6"><h1 className="text-3xl font-bold">Memory (Coming Soon)</h1></div>;
      case "settings":
        return <div className="p-6"><h1 className="text-3xl font-bold">Settings (Coming Soon)</h1></div>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
      {/* Sidebar */}
      <div className="fixed left-0 top-0 h-full w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-4">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Observational Memory</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">v2.0.0 Rust</p>
        </div>

        <nav className="space-y-2">
          {[
            { id: "dashboard", label: "Dashboard", icon: "📊" },
            { id: "sessions", label: "Sessions", icon: "📁" },
            { id: "search", label: "Search", icon: "🔍" },
            { id: "analytics", label: "Analytics", icon: "📈" },
            { id: "tools", label: "Tools", icon: "🛠️" },
            { id: "memory", label: "Memory", icon: "🧠" },
            { id: "settings", label: "Settings", icon: "⚙️" },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentPage(item.id as Page)}
              className={`w-full text-left px-4 py-2 rounded transition ${
                currentPage === item.id
                  ? "bg-blue-500 text-white"
                  : "hover:bg-gray-100 dark:hover:bg-gray-700"
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {renderPage()}
      </div>
    </div>
  );
}

export default App;
