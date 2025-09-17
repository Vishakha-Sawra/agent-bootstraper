// app/layout.tsx
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Agentic UI",
  description: "Agentic DevOps Platform with FastAPI + Next.js + Tailwind",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen flex flex-col">
        {/* Navbar */}
        <header className="bg-blue-600 text-white p-4 shadow">
          <h1 className="text-xl font-bold">⚡ Agentic Platform</h1>
        </header>

        {/* Main Content */}
        <main className="flex-1 container mx-auto p-6">{children}</main>

        {/* Footer */}
        <footer className="bg-gray-800 text-gray-300 p-4 text-center text-sm">
          Agentic Platform © {new Date().getFullYear()}
        </footer>
      </body>
    </html>
  );
}
