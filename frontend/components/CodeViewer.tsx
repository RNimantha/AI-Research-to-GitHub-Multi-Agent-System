"use client";
import { useState } from "react";
import { C, F } from "../lib/design";

interface GeneratedFile {
  path: string;
  purpose: string;
  content: string;
}

export default function CodeViewer({ files }: { files: GeneratedFile[] }) {
  const [activeIdx, setActiveIdx] = useState(0);

  if (!files || files.length === 0) {
    return <p style={{ color: C.textMuted, fontSize: "0.85rem", fontStyle: "italic" }}>No files generated yet.</p>;
  }

  const active = files[activeIdx];

  return (
    <div style={styles.container}>
      <div style={styles.tabs}>
        {files.map((f, i) => (
          <button
            key={i}
            onClick={() => setActiveIdx(i)}
            style={{ ...styles.tab, ...(i === activeIdx ? styles.tabActive : {}) }}
            title={f.path}
          >
            {f.path.split("/").pop()}
          </button>
        ))}
      </div>
      <div style={styles.fileBar}>
        <span style={styles.filePath}>{active.path}</span>
        {active.purpose && <span style={styles.purpose}>{active.purpose}</span>}
        <span style={styles.lineCount}>
          {active.content.split("\n").length} lines
        </span>
      </div>
      <pre style={styles.code}>
        <code>{active.content}</code>
      </pre>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { border: `1px solid ${C.border}`, borderRadius: 7, overflow: "hidden" },
  tabs: { display: "flex", flexWrap: "wrap", background: C.bgSubtle, borderBottom: `1px solid ${C.border}`, overflowX: "auto" },
  tab: { padding: "0.4rem 0.75rem", border: "none", background: "transparent", cursor: "pointer", fontFamily: F.mono, fontSize: "0.78rem", color: C.textMuted, borderRight: `1px solid ${C.border}`, whiteSpace: "nowrap" as const, flexShrink: 0 },
  tabActive: { background: C.bg, color: C.text, fontWeight: 600, borderBottom: `2px solid ${C.blue}` },
  fileBar: { display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.35rem 0.75rem", background: C.bgSubtle, borderBottom: `1px solid ${C.border}`, flexWrap: "wrap" },
  filePath: { fontFamily: F.mono, fontWeight: 600, fontSize: "0.78rem", color: C.blue },
  purpose: { fontSize: "0.75rem", color: C.textMuted, flex: 1 },
  lineCount: { fontSize: "0.72rem", color: C.textMuted, marginLeft: "auto" },
  code: { margin: 0, padding: "0.9rem 1rem", background: "#0D1117", color: "#E6EDF3", overflowX: "auto", fontSize: "0.8rem", fontFamily: F.mono, lineHeight: 1.6, maxHeight: 520, overflowY: "auto" as const },
};
