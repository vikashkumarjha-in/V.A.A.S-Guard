import React, { useState, useEffect, useRef } from 'react';
import { Shield, AlertTriangle, Activity, Moon, Sun, Terminal } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const ThreatBadge = ({ severity }) => {
  const colors = {
    Low: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
    Medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
    High: "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300",
    Critical: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  };
  return (
    <span className={cn("px-2 py-1 rounded-full text-xs font-medium", colors[severity] || colors.Medium)}>
      {severity}
    </span>
  );
};

function App() {
  const [logs, setLogs] = useState([]);
  const [isDark, setIsDark] = useState(true);
  const [connected, setConnected] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    connectWS();
    return () => ws.current?.close();
  }, []);

  const connectWS = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_WS_URL
      ? import.meta.env.VITE_WS_URL.replace('https://', '').replace('wss://', '')
      : window.location.hostname === 'localhost'
        ? 'localhost:10000'
        : window.location.hostname;
    ws.current = new WebSocket(`${protocol}//${host}/ws/logs`);

    ws.current.onopen = () => setConnected(true);
    ws.current.onclose = () => {
      setConnected(false);
      setTimeout(connectWS, 3000);
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs((prev) => {
        const index = prev.findIndex(l => l.event_id === data.event_id);
        if (index !== -1) {
          const newLogs = [...prev];
          newLogs[index] = data;
          return newLogs;
        }
        return [data, ...prev].slice(0, 100);
      });
    };
  };

  const toggleDarkMode = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <div className={cn("min-h-screen w-full transition-colors duration-200",
      isDark ? "bg-slate-950 text-slate-100" : "bg-slate-50 text-slate-900")}>

      {/* Navigation */}
      <nav className={cn("border-b px-6 py-4 flex justify-between items-center",
        isDark ? "border-slate-800 bg-slate-900/50" : "border-slate-200 bg-white")}>
        <div className="flex items-center gap-2">
          <Shield className="text-indigo-500 w-8 h-8" />
          <h1 className="text-xl font-bold tracking-tight">V.A.A.S GUARD</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={cn("w-2 h-2 rounded-full", connected ? "bg-green-500" : "bg-red-500")} />
            <span className="text-sm font-medium">{connected ? "Connected" : "Disconnected"}</span>
          </div>
          <button onClick={toggleDarkMode} className="p-2 rounded-lg hover:bg-slate-800/50">
            {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </div>
      </nav>

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className={cn("p-4 rounded-xl border", isDark ? "bg-slate-900 border-slate-800" : "bg-white border-slate-200")}>
            <div className="flex items-center gap-3 text-slate-400 mb-2">
              <Activity className="w-4 h-4" />
              <span className="text-sm font-medium">Total Threats</span>
            </div>
            <div className="text-2xl font-bold">{logs.length}</div>
          </div>
          <div className={cn("p-4 rounded-xl border", isDark ? "bg-slate-900 border-slate-800" : "bg-white border-slate-200")}>
            <div className="flex items-center gap-3 text-red-400 mb-2">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm font-medium">Critical Issues</span>
            </div>
            <div className="text-2xl font-bold">{logs.filter(l => l.severity === 'Critical').length}</div>
          </div>
          <div className={cn("p-4 rounded-xl border", isDark ? "bg-slate-900 border-slate-800" : "bg-white border-slate-200")}>
            <div className="flex items-center gap-3 text-indigo-400 mb-2">
              <Terminal className="w-4 h-4" />
              <span className="text-sm font-medium">System Status</span>
            </div>
            <div className="text-2xl font-bold">Protected</div>
          </div>
        </div>

        {/* Log Table */}
        <div className={cn("rounded-xl border overflow-hidden", isDark ? "bg-slate-900 border-slate-800" : "bg-white border-slate-200")}>
          <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
            <h2 className="font-semibold">Security Events</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className={cn("text-xs uppercase tracking-wider", isDark ? "bg-slate-800/50 text-slate-400" : "bg-slate-50 text-slate-500")}>
                  <th className="px-6 py-3 font-semibold">Timestamp</th>
                  <th className="px-6 py-3 font-semibold">Type</th>
                  <th className="px-6 py-3 font-semibold">IP Address</th>
                  <th className="px-6 py-3 font-semibold">Method/Path</th>
                  <th className="px-6 py-3 font-semibold">Severity</th>
                  <th className="px-6 py-3 font-semibold">AI Analysis</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-10 text-center text-slate-500">
                      Waiting for incoming threats...
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.event_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-6 py-4 text-sm font-mono">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className="font-semibold">{log.threat_type}</span>
                      </td>
                      <td className="px-6 py-4 text-sm font-mono">{log.client_ip}</td>
                      <td className="px-6 py-4 text-sm">
                        <div className="flex items-center gap-2">
                          <span className="text-indigo-400 font-bold">{log.method}</span>
                          <span className="text-slate-400 truncate max-w-[150px]">{log.path}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <ThreatBadge severity={log.severity} />
                      </td>
                      <td className="px-6 py-4 text-sm italic text-slate-400">
                        {log.explanation || "Analyzing..."}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
