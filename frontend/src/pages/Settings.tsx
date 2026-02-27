import { useState } from "react";

export default function Settings() {
  const [openclawInstalled, setOpenclawInstalled] = useState(false);
  const [theme, setTheme] = useState("dark");
  const [language, setLanguage] = useState("zh");
  const [autoProcess, setAutoProcess] = useState(true);
  const [minMessages, setMinMessages] = useState(10);

  const handleInstallOpenclaw = () => {
    // Simulate installation
    setTimeout(() => {
      setOpenclawInstalled(true);
    }, 2000);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>

      {/* OpenClaw Integration */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <h2 className="text-xl font-bold">OpenClaw Integration</h2>

        {openclawInstalled ? (
          <div className="p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-bold text-green-800 dark:text-green-200">
                  ✅ Installed
                </div>
                <div className="text-sm text-green-600 dark:text-green-400 mt-1">
                  Hook is active and processing sessions
                </div>
              </div>
              <button className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition">
                Uninstall
              </button>
            </div>

            <div className="mt-4 space-y-3">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Minimum Messages: {minMessages}
                </label>
                <input
                  type="range"
                  min="5"
                  max="50"
                  value={minMessages}
                  onChange={(e) => setMinMessages(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoProcess}
                  onChange={(e) => setAutoProcess(e.target.checked)}
                  className="mr-2"
                />
                <label className="text-sm">Enable Auto Processing</label>
              </div>

              <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition">
                Save Configuration
              </button>
            </div>
          </div>
        ) : (
          <div className="p-4 bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-lg">
            <div className="font-bold text-yellow-800 dark:text-yellow-200 mb-2">
              ⚠️ Not Installed
            </div>
            <div className="text-sm text-yellow-600 dark:text-yellow-400 mb-4">
              Install the OpenClaw hook to enable automatic session processing
            </div>
            <button
              onClick={handleInstallOpenclaw}
              className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
            >
              Install Now
            </button>
          </div>
        )}
      </div>

      {/* Data Management */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <h2 className="text-xl font-bold">Data Management</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
            <div className="font-bold mb-1">Export Sessions</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Export all sessions as JSON or CSV
            </div>
          </button>

          <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
            <div className="font-bold mb-1">Import Data</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Import sessions from file
            </div>
          </button>

          <button className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 transition text-left">
            <div className="font-bold mb-1">Create Backup</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Backup all data to ZIP file
            </div>
          </button>

          <button className="p-4 border-2 border-red-200 dark:border-red-700 rounded-lg hover:border-red-500 transition text-left">
            <div className="font-bold mb-1 text-red-500">Clear Data</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Delete all observations (irreversible)
            </div>
          </button>
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <h2 className="text-xl font-bold">System Status</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Total Observations
            </div>
            <div className="text-2xl font-bold mt-1">1,234</div>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Storage Used
            </div>
            <div className="text-2xl font-bold mt-1">45.2 MB</div>
          </div>

          <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Vector Embeddings
            </div>
            <div className="text-2xl font-bold mt-1">856</div>
          </div>
        </div>

        <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
          <div className="flex items-center justify-between mb-2">
            <span className="font-medium">Database Size</span>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              32.1 MB / 100 MB
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full"
              style={{ width: "32%" }}
            ></div>
          </div>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow space-y-4">
        <h2 className="text-xl font-bold">Configuration</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            >
              <option value="zh">简体中文</option>
              <option value="en">English</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Theme</label>
            <select
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>

          <div className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div>
              <div className="font-medium">Auto Backup</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                Backup data every 24 hours
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <button className="w-full px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
            Save All Settings
          </button>
        </div>
      </div>
    </div>
  );
}
