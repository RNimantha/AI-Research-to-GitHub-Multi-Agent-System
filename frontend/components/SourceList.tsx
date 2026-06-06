"use client";
import { C, F } from "../lib/design";

interface Source {
  title: string;
  url: string;
  source_type?: string;
  published_date?: string;
  credibility_score?: number;
  summary?: string;
}

export default function SourceList({ sources }: { sources: Source[] }) {
  if (!sources || sources.length === 0) {
    return <p style={{ color: C.textMuted, fontSize: "0.85rem", fontStyle: "italic" }}>No sources yet.</p>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
      {sources.map((s, i) => (
        <div key={i} style={styles.card}>
          <div style={styles.header}>
            <a href={s.url} target="_blank" rel="noreferrer" style={styles.title}>
              {s.title || s.url}
            </a>
            <div style={{ display: "flex", gap: "0.3rem", alignItems: "center", flexShrink: 0 }}>
              {s.source_type && <span style={styles.typeTag}>{s.source_type}</span>}
              {s.credibility_score != null && (
                <span style={{
                  ...styles.credTag,
                  color: s.credibility_score >= 0.8 ? C.green : s.credibility_score >= 0.6 ? C.amber : C.red,
                  background: s.credibility_score >= 0.8 ? C.greenLight : s.credibility_score >= 0.6 ? C.amberLight : C.redLight,
                }}>
                  {(s.credibility_score * 10).toFixed(1)}/10
                </span>
              )}
            </div>
          </div>
          {s.published_date && <p style={styles.meta}>{s.published_date}</p>}
          {s.summary && <p style={styles.summary}>{s.summary}</p>}
          <p style={styles.url}>{s.url}</p>
        </div>
      ))}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  card: { border: `1px solid ${C.border}`, borderRadius: 7, padding: "0.7rem 0.85rem", background: C.bgSubtle },
  header: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.2rem" },
  title: { fontWeight: 600, color: C.blue, textDecoration: "none", fontSize: "0.88rem", flex: 1, lineHeight: 1.35 },
  typeTag: { fontSize: "0.68rem", background: C.bgMuted, color: C.textSec, padding: "0.1rem 0.35rem", borderRadius: 4, whiteSpace: "nowrap" as const },
  credTag: { fontSize: "0.68rem", padding: "0.1rem 0.35rem", borderRadius: 4, fontWeight: 700, whiteSpace: "nowrap" as const },
  meta: { margin: "0.1rem 0 0", fontSize: "0.72rem", color: C.textMuted },
  summary: { margin: "0.3rem 0 0.2rem", fontSize: "0.82rem", color: C.textSec, lineHeight: 1.4 },
  url: { margin: "0.2rem 0 0", fontSize: "0.72rem", color: C.textMuted, fontFamily: F.mono, wordBreak: "break-all" as const },
};
