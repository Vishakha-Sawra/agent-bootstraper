"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const [repoUrl, setRepoUrl] = useState("");
  const [branch, setBranch] = useState("main");
  const router = useRouter();

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    const res = await fetch("http://127.0.0.1:8080/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: repoUrl, branch }),
    });
    const data = await res.json();
    localStorage.setItem("scan", JSON.stringify(data));
    router.push("/plan");
  };

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">Scan Repository</h1>
      <form onSubmit={handleScan} className="space-y-4">
        <div>
          <label className="block mb-1">Repository URL:</label>
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            className="border p-2 w-full rounded"
            required
          />
        </div>
        <div>
          <label className="block mb-1">Branch:</label>
          <input
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            className="border p-2 w-full rounded"
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Scan
        </button>
      </form>
    </div>
  );
}
