"use client";
import { useRouter } from "next/navigation";

export default function Results() {
  const plan = JSON.parse(localStorage.getItem("plan") || "[]");
  const scan = JSON.parse(localStorage.getItem("scan") || "{}");
  const router = useRouter();

  const handleExecute = async () => {
    const res = await fetch("http://127.0.0.1:8080/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(plan),
    });
    const data = await res.json();
    localStorage.setItem("execution", JSON.stringify(data));
    router.push("/execute");
  };

  const downloadPlan = () => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const filename = `execution_plan_${timestamp}.md`;
    
    let markdown = `# Execution Plan Report\n\nGenerated on: ${new Date().toLocaleString()}\n\n## Project Information\n\n`;
    
    // Add scan information
    if (scan && Object.keys(scan).length > 0) {
      markdown += `**Repository:** ${scan.repo_url || 'Unknown'}\n`;
      markdown += `**Branch:** ${scan.branch || 'Unknown'}\n`;
      markdown += `**Project Name:** ${scan.project_name || 'Unknown'}\n\n`;
      
      if (scan.languages && scan.languages.length > 0) {
        markdown += `**Languages:** ${scan.languages.join(', ')}\n`;
      }
      if (scan.frameworks && scan.frameworks.length > 0) {
        markdown += `**Frameworks:** ${scan.frameworks.join(', ')}\n`;
      }
      if (scan.database) {
        markdown += `**Database:** ${scan.database}\n`;
      }
      markdown += "\n";
    }
    
    // Add plan steps
    if (plan && plan.length > 0) {
      markdown += "## Execution Plan Steps\n\n";
      plan.forEach((step: any, i: number) => {
        markdown += `### Step ${i + 1}: ${step.tool || 'Unknown Tool'}\n\n`;
        markdown += `**File Path:** \`${step.args?.file_path || 'N/A'}\`\n\n`;
        
        if (step.args?.content) {
          markdown += "**Generated Content:**\n\n";
          markdown += `\`\`\`\n${step.args.content}\n\`\`\`\n\n`;
        }
        
        if (step.success_check) {
          markdown += `**Success Check:** ${step.success_check}\n\n`;
        }
        
        if (step.on_fail) {
          markdown += `**On Failure:** ${step.on_fail}\n\n`;
        }
        
        markdown += "---\n\n";
      });
    }
    
    // Download the file
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="p-10">
      <h1 className="text-3xl font-bold mb-6">📋 Execution Plan</h1>
      {plan.map((step: any, i: number) => (
        <div key={i} className="border p-4 mb-4 rounded bg-gray-50">
          <h2 className="font-semibold">{step.tool}</h2>
          {step.args?.file_path && (
            <p className="text-sm text-gray-600">{step.args.file_path}</p>
          )}
          {step.args?.content && (
            <pre className="bg-white p-2 mt-2 rounded border">
              {step.args.content}
            </pre>
          )}
          {step.success_check && (
            <p className="text-green-600">✅ {step.success_check}</p>
          )}
          {step.on_fail && <p className="text-red-600">⚠️ {step.on_fail}</p>}
        </div>
      ))}
      
      <div className="flex gap-4 mt-6">
        <button
          onClick={downloadPlan}
          className="bg-green-600 text-white px-6 py-3 rounded hover:bg-green-700 font-medium"
        >
          📥 Download Plan as Markdown
        </button>
        
        <button
          onClick={handleExecute}
          className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 font-medium"
        >
          🚀 Execute Plan
        </button>
      </div>
    </div>
  );
}
