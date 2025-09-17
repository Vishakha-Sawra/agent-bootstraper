"use client";

import { useEffect, useState } from "react";

export default function Execution() {
  const [exec, setExec] = useState<any>(null);

  useEffect(() => {
    const stored = localStorage.getItem("execution");
    if (stored) {
      console.log("Loaded execution JSON:", stored);
      setExec(JSON.parse(stored));
    }
  }, []);

  if (!exec) {
    return <div>Loading execution results…</div>;
  }

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">Execution Results</h1>

      <h2 className="text-xl font-semibold mb-4">Statuses</h2>
      {exec.execution_results?.map((r: any, i: number) => (
        <div
          key={i}
          className={`p-3 mb-2 rounded ${
            r.status === "success"
              ? "bg-green-100 text-green-700"
              : r.status === "failed"
              ? "bg-red-100 text-red-700"
              : "bg-yellow-100 text-yellow-700"
          }`}
        >
          <strong>{r.tool}</strong>: {r.status}
          <p>{r.details}</p>
        </div>
      ))}

      <h2 className="text-xl font-semibold mt-6 mb-4">Generated Files</h2>
      {exec.files && exec.files.length > 0 ? (
        exec.files.map((file: any, i: number) => (
          <div key={i} className="mb-4 border rounded p-4 bg-gray-50">
            <h3 className="font-semibold">
              {file.tool} - {file.file_path}
            </h3>
            <pre className="bg-white p-2 rounded border mt-2 whitespace-pre-wrap">
              {file.content}
            </pre>
          </div>
        ))
      ) : (
        <div>No generated files to display.</div>
      )}
    </div>
  );
}