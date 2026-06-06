import type { Metadata } from "next";
import Nav from "../components/Nav";
import { C, F } from "../lib/design";

export const metadata: Metadata = {
  title: "ARAS — AI Research Operations",
  description: "AI Research-to-GitHub Multi-Agent System",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{
        margin: 0,
        background: C.bgSubtle,
        color: C.text,
        fontFamily: F.sans,
        fontSize: 14,
        lineHeight: 1.5,
        minHeight: "100vh",
      }}>
        <Nav />
        <main style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem 1.5rem" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
