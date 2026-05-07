import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MedLens | Clinical Evidence Search",
  description:
    "Search 30K+ PubMed abstracts with AI-powered hybrid retrieval and citation-grounded synthesis",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen bg-slate-950`}>
        {children}
      </body>
    </html>
  );
}
