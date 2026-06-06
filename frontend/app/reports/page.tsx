"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/api";
import { C, F } from "../../lib/design";

interface Report {
  topic_slug: string;
  topic_name: string;
  one_liner?: string;
  tags?: string[];
  eval_score?: number;
  github_url?: string;
  created_at?: string;
}

export default function ReportsList() {
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");

  useEffect(() => {
    api.listReports()
      .then((d: any) => setReports(d.reports ?? []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = reports.filter((r) =>
    !query || r.topic_name.toLowerCase().includes(query.toLowerCase()) ||
    (r.tags ?? []).some((t) => t.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <div>
      <div style={styles.pageHeader}>
        <h1 style={styles.pageTitle}>Reports</h1>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search reports…"
          style={styles.searchInput}
        />
      </div>

      {loading && <p style={{ color: C.textMuted, fontSize: "0.85rem" }}>Loading…</p>}
      {error && <p style={{ color: C.red, fontSize: "0.85rem" }}>{error}</p>}
      {!loading && filtered.length === 0 && !error && (
        <div style={styles.empty}>
          <p style={{ margin: 0, color: C.textMuted, fontSize: "0.85rem" }}>
            {query ? "No matching reports." : "No published reports yet."}
          </p>
        </div>
      )}

      <div style={styles.grid}>
        {filtered.map((r) => (
          <Link key={r.topic_slug} href={`/reports/${r.topic_slug}`} style={{ textDecoration: "none" }}>
            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <span style={styles.slug}>{r.topic_slug}</span>
                {r.eval_score != null && (
                  <span style={{ ...styles.score, color: r.eval_score >= 8 ? C.green : r.eval_score >= 7 ? C.amber : C.red }}>
                    {r.eval_score.toFixed(1)}/10
                  </span>
                )}
              </div>
              <p style={styles.name}>{r.topic_name}</p>
              {r.one_liner && <p style={styles.oneLiner}>{r.one_liner}</p>}
              <div style={styles.cardFooter}>
                {(r.tags ?? []).map((t) => <Tag key={t} label={t} />)}
                {r.github_url && <Tag label="GitHub" color={C.green} bg={`${C.green}15`} />}
                {r.created_at && (
                  <span style={styles.date}>{new Date(r.created_at).toLocaleDateString()}</span>
                )}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

function Tag({ label, color, bg }: { label: string; color?: string; bg?: string }) {
  return (
    <span style={{
      fontSize: "0.72rem",
      background: bg ?? C.bgMuted,
      color: color ?? C.textSec,
      padding: "0.1rem 0.4rem",
      borderRadius: 4,
      fontWeight: 500,
    }}>
      {label}
    </span>
  );
}

const styles: Record<string, React.CSSProperties> = {
  pageHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem", flexWrap: "wrap", gap: "0.75rem" },
  pageTitle: { margin: 0, fontSize: "1.3rem", fontWeight: 700, color: C.text },
  searchInput: { padding: "0.45rem 0.75rem", border: `1px solid ${C.border}`, borderRadius: 6, fontFamily: F.sans, fontSize: "0.85rem", color: C.text, background: C.bg, outline: "none", minWidth: 240 },
  empty: { padding: "2.5rem", textAlign: "center", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8 },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "0.75rem" },
  card: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "0.9rem 1rem", cursor: "pointer", height: "100%", boxSizing: "border-box" as const, display: "flex", flexDirection: "column" },
  cardHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" },
  slug: { fontFamily: F.mono, fontSize: "0.72rem", color: C.textMuted },
  score: { fontWeight: 700, fontSize: "0.85rem" },
  name: { margin: "0 0 0.3rem", fontWeight: 600, fontSize: "0.95rem", color: C.text },
  oneLiner: { margin: "0 0 0.6rem", fontSize: "0.82rem", color: C.textSec, lineHeight: 1.45, flex: 1 },
  cardFooter: { display: "flex", gap: "0.3rem", flexWrap: "wrap", alignItems: "center", marginTop: "auto" },
  date: { marginLeft: "auto", fontSize: "0.72rem", color: C.textMuted },
};
