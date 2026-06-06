"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/api";
import { C, F, statusColor, statusBg } from "../../lib/design";

interface Run {
  run_id: string;
  status: string;
  approved_topic?: string;
  selected_topic?: { title: string };
  input_topic?: string;
  eval_score?: number;
  created_at?: string;
  estimated_cost_usd?: number;
}

export default function RunsList() {
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "active" | "complete" | "failed">("all");

  useEffect(() => {
    api.listRuns()
      .then((d: any) => setRuns(d.runs ?? []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = runs.filter((r) => {
    if (filter === "active") return !["complete", "failed", "pending"].includes(r.status);
    if (filter === "complete") return r.status === "complete";
    if (filter === "failed") return r.status === "failed";
    return true;
  });

  return (
    <div>
      <div style={styles.pageHeader}>
        <h1 style={styles.pageTitle}>Research Runs</h1>
        <Link href="/dashboard" style={styles.newBtn}>+ New Run</Link>
      </div>

      <div style={styles.filters}>
        {(["all", "active", "complete", "failed"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{ ...styles.filterBtn, ...(filter === f ? styles.filterBtnActive : {}) }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <span style={styles.count}>{filtered.length} runs</span>
      </div>

      {loading && <EmptyState msg="Loading…" />}
      {error && <p style={{ color: C.red, fontSize: "0.85rem" }}>{error}</p>}
      {!loading && filtered.length === 0 && !error && (
        <EmptyState msg="No runs found." cta={{ label: "Start a run", href: "/dashboard" }} />
      )}

      {!loading && (
        <div style={styles.table}>
          {filtered.map((run) => {
            const topic = run.approved_topic ?? run.selected_topic?.title ?? run.input_topic ?? "Auto-discover";
            const sc = statusColor(run.status);
            const sb = statusBg(run.status);
            const isAwaiting = run.status.startsWith("awaiting_");

            return (
              <Link key={run.run_id} href={`/runs/${run.run_id}`} style={{ textDecoration: "none" }}>
                <div style={styles.row}>
                  <div style={styles.rowLeft}>
                    <span style={{ ...styles.statusBadge, color: sc, background: sb }}>
                      {run.status.replace(/_/g, " ")}
                    </span>
                    {isAwaiting && (
                      <span style={styles.actionNeeded}>Approval needed</span>
                    )}
                  </div>
                  <p style={styles.rowTopic}>{topic}</p>
                  <div style={styles.rowMeta}>
                    <span style={styles.rowId}>{run.run_id.slice(0, 8)}</span>
                    {run.eval_score != null && (
                      <span style={{ fontWeight: 700, fontSize: "0.8rem", color: run.eval_score >= 8 ? C.green : run.eval_score >= 7 ? C.amber : C.red }}>
                        {run.eval_score.toFixed(1)}/10
                      </span>
                    )}
                    {run.estimated_cost_usd != null && (
                      <span style={styles.metaVal}>${run.estimated_cost_usd.toFixed(4)}</span>
                    )}
                    {run.created_at && (
                      <span style={{ ...styles.metaVal, marginLeft: "auto" }}>
                        {new Date(run.created_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

function EmptyState({ msg, cta }: { msg: string; cta?: { label: string; href: string } }) {
  return (
    <div style={{ padding: "2.5rem", textAlign: "center", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8 }}>
      <p style={{ margin: "0 0 0.5rem", color: C.textMuted, fontSize: "0.85rem" }}>{msg}</p>
      {cta && <Link href={cta.href} style={{ fontSize: "0.85rem", color: C.blue }}>{cta.label} →</Link>}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  pageHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" },
  pageTitle: { margin: 0, fontSize: "1.3rem", fontWeight: 700, color: C.text },
  newBtn: { padding: "0.45rem 0.9rem", background: C.blue, color: "#fff", textDecoration: "none", borderRadius: 6, fontSize: "0.85rem", fontWeight: 600, fontFamily: F.sans },
  filters: { display: "flex", gap: "0.25rem", marginBottom: "0.75rem", alignItems: "center" },
  filterBtn: { padding: "0.35rem 0.7rem", border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", fontSize: "0.8rem", background: C.bg, color: C.textSec, fontFamily: F.sans },
  filterBtnActive: { background: C.bgMuted, color: C.text, fontWeight: 600, borderColor: C.borderStrong },
  count: { marginLeft: "auto", fontSize: "0.78rem", color: C.textMuted },
  table: { display: "flex", flexDirection: "column", gap: "0.35rem" },
  row: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 7, padding: "0.7rem 0.9rem", cursor: "pointer", display: "flex", flexDirection: "column", gap: "0.2rem" },
  rowLeft: { display: "flex", alignItems: "center", gap: "0.4rem" },
  statusBadge: { fontSize: "0.72rem", padding: "0.15rem 0.45rem", borderRadius: 4, fontWeight: 600, textTransform: "capitalize" as const },
  actionNeeded: { fontSize: "0.68rem", background: C.amberLight, color: C.amber, padding: "0.1rem 0.4rem", borderRadius: 3, fontWeight: 700 },
  rowTopic: { margin: 0, fontWeight: 500, fontSize: "0.9rem", color: C.text },
  rowMeta: { display: "flex", gap: "0.75rem", alignItems: "center", flexWrap: "wrap" },
  rowId: { fontFamily: F.mono, fontSize: "0.72rem", color: C.textMuted },
  metaVal: { fontSize: "0.78rem", color: C.textMuted },
};
