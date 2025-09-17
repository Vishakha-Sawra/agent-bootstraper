"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Plan() {
  const [scan, setScan] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    const stored = localStorage.getItem("scan");
    if (stored) {
      setScan(JSON.parse(stored));
    }
  }, []);

  const handleGeneratePlan = async () => {
    if (!scan) return;

    const res = await fetch("http://127.0.0.1:8080/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scan),
    });

    const plan = await res.json();
    localStorage.setItem("plan", JSON.stringify(plan));
    router.push("/results");
  };

  if (!scan) {
    return <div>⚠️ No scan data found. Go back and scan a repo first.</div>;
  }

  return (
    <div>
      <h1>⚡ Agentic Platform</h1>
      <h2>Scan Summary</h2>
      <pre>{JSON.stringify(scan, null, 2)}</pre>

      <button
        onClick={handleGeneratePlan}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        Generate Plan
      </button>
    </div>
  );
}
