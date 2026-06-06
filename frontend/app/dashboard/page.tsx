"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import Link from "next/link";
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

export default function Dashboard() {
  const router = useRouter();
  const [health, setHealth] = useState<{ status: string } | null>(null);
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [runs, setRuns] = useState<Run[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "unreachable" }));
    api.listRuns().then((d: any) => setRuns((d.runs ?? []).slice(0, 8))).catch(() => {});
  }, []);

  const startRun = async () => {
    setLoading(true);
    setError("");
    try {
      const result = await api.createRun(topic || undefined) as { run_id: string };
      router.push(`/runs/${result.run_id}`);
    } catch (e: any) {
      setError(e.message);
      setLoading(false);
    }
  };

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") startRun();
  };

  const activeRuns = runs.filter((r) => !["complete", "failed"].includes(r.status));
  const completedRuns = runs.filter((r) => r.status === "complete");
  const avgScore = completedRuns.length
    ? completedRuns.reduce((a, r) => a + (r.eval_score ?? 0), 0) / completedRuns.length
    : null;

  return (
    <div>
      {/* Page title */}
      <div style={styles.pageHeader}>
        <div>
          <h1 style={styles.pageTitle}>Research Operations</h1>
          <p style={styles.pageDesc}>
            Discover AI trends, generate reports and POC projects, publish to GitHub.
          </p>
        </div>
        <div style={styles.backendStatus}>
          <span style={{
            ...styles.statusDot,
            background: health?.status === "ok" ? C.green : health?.status === "unreachable" ? C.red : C.amber,
          }} />
          <span style={{ fontSize: "0.8rem", color: C.textSec }}>
            Backend {health?.status ?? "checking…"}
          </span>
        </div>
      </div>

      {/* Stats row */}
      <div style={styles.statsRow}>
        <Stat label="Total Runs" value={runs.length} />
        <Stat label="Active" value={activeRuns.length} accent={activeRuns.length > 0 ? C.blue : undefined} />
        <Stat label="Completed" value={completedRuns.length} accent={C.green} />
        <Stat label="Avg Score" value={avgScore != null ? `${avgScore.toFixed(1)}/10` : "—"} />
      </div>

      {/* New run card */}
      <div style={styles.card}>
        <h2 style={styles.cardTitle}>Start Research Run</h2>
        <p style={styles.cardDesc}>
          Provide an AI topic for targeted research, or leave blank to let the discovery agent find trending topics.
        </p>
        <div style={styles.inputRow}>
          <input
            ref={inputRef}
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={handleKey}
            placeholder="e.g. 'LangGraph multi-agent patterns' or leave blank for auto-discovery"
            style={styles.input}
            disabled={loading}
            autoFocus
          />
          <button onClick={startRun} disabled={loading} style={styles.primaryBtn}>
            {loading ? "Starting…" : "Start Run"}
          </button>
        </div>
        {error && <p style={styles.errorMsg}>{error}</p>}
        <p style={styles.hint}>
          Press Enter to start • The pipeline will pause at each approval gate
        </p>
      </div>

      {/* Active runs */}
      {activeRuns.length > 0 && (
        <section style={styles.section}>
          <div style={styles.sectionHeader}>
            <h2 style={styles.sectionTitle}>Active Runs</h2>
            <span style={styles.liveDot} />
          </div>
          <div style={styles.runList}>
            {activeRuns.map((run) => <RunRow key={run.run_id} run={run} />)}
          </div>
        </section>
      )}

      {/* Recent runs */}
      {runs.length > 0 && (
        <section style={styles.section}>
          <div style={styles.sectionHeader}>
            <h2 style={styles.sectionTitle}>Recent Runs</h2>
            <Link href="/runs" style={styles.viewAll}>View all →</Link>
          </div>
          <div style={styles.runList}>
            {runs.slice(0, 5).map((run) => <RunRow key={run.run_id} run={run} />)}
          </div>
        </section>
      )}
    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div style={statStyles.card}>
      <p style={statStyles.label}>{label}</p>
      <p style={{ ...statStyles.value, color: accent ?? C.text }}>{value}</p>
    </div>
  );
}

function RunRow({ run }: { run: Run }) {
  const topic = run.approved_topic ?? run.selected_topic?.title ?? run.input_topic ?? "Auto-discover";
  const sc = statusColor(run.status);
  const sb = statusBg(run.status);
  const isAwaiting = run.status.startsWith("awaiting_");

  return (
    <Link href={`/runs/${run.run_id}`} style={{ textDecoration: "none" }}>
      <div style={rowStyles.row}>
        <div style={rowStyles.left}>
          <span style={{ ...rowStyles.badge, color: sc, background: sb }}>
            {run.status.replace(/_/g, " ")}
          </span>
          {isAwaiting && <span style={rowStyles.actionTag}>Action needed</span>}
        </div>
        <p style={rowStyles.topic}>{topic}</p>
        <div style={rowStyles.meta}>
          <span style={rowStyles.id}>{run.run_id.slice(0, 8)}</span>
          {run.eval_score != null && (
            <span style={{ ...rowStyles.score, color: run.eval_score >= 8 ? C.green : run.eval_score >= 7 ? C.amber : C.red }}>
              {run.eval_score.toFixed(1)}/10
            </span>
          )}
          {run.created_at && (
            <span style={rowStyles.date}>{new Date(run.created_at).toLocaleDateString()}</span>
          )}
        </div>
      </div>
    </Link>
  );
}

const styles: Record<string, React.CSSProperties> = {
  pageHeader: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem", flexWrap: "wrap", gap: "1rem" },
  pageTitle: { margin: "0 0 0.25rem", fontSize: "1.4rem", fontWeight: 700, color: C.text },
  pageDesc: { margin: 0, color: C.textSec, fontSize: "0.9rem" },
  backendStatus: { display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.4rem 0.75rem", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6 },
  statusDot: { width: 8, height: 8, borderRadius: "50%", flexShrink: 0 },
  statsRow: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "0.75rem", marginBottom: "1.25rem" },
  card: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "1.5rem", marginBottom: "1.5rem" },
  cardTitle: { margin: "0 0 0.3rem", fontSize: "1rem", fontWeight: 600, color: C.text },
  cardDesc: { margin: "0 0 1rem", color: C.textSec, fontSize: "0.85rem" },
  inputRow: { display: "flex", gap: "0.5rem" },
  input: {
    flex: 1,
    padding: "0.6rem 0.75rem",
    border: `1px solid ${C.border}`,
    borderRadius: 6,
    fontFamily: F.sans,
    fontSize: "0.9rem",
    color: C.text,
    background: C.bg,
    outline: "none",
  },
  primaryBtn: {
    padding: "0.6rem 1.25rem",
    background: C.blue,
    color: "#fff",
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "0.9rem",
    fontFamily: F.sans,
    flexShrink: 0,
  },
  errorMsg: { margin: "0.5rem 0 0", color: C.red, fontSize: "0.85rem" },
  hint: { margin: "0.5rem 0 0", fontSize: "0.78rem", color: C.textMuted },
  section: { marginBottom: "1.5rem" },
  sectionHeader: { display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" },
  sectionTitle: { margin: 0, fontSize: "0.9rem", fontWeight: 600, color: C.text },
  liveDot: { width: 7, height: 7, borderRadius: "50%", background: C.blue, animation: "pulse 2s infinite" },
  viewAll: { marginLeft: "auto", fontSize: "0.8rem", color: C.blue, textDecoration: "none" },
  runList: { display: "flex", flexDirection: "column", gap: "0.4rem" },
};

const statStyles: Record<string, React.CSSProperties> = {
  card: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "0.75rem 1rem" },
  label: { margin: "0 0 0.2rem", fontSize: "0.75rem", color: C.textMuted, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" },
  value: { margin: 0, fontSize: "1.4rem", fontWeight: 700 },
};

const rowStyles: Record<string, React.CSSProperties> = {
  row: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "0.65rem 0.9rem", display: "flex", flexDirection: "column", gap: "0.2rem", cursor: "pointer" },
  left: { display: "flex", alignItems: "center", gap: "0.4rem" },
  badge: { fontSize: "0.72rem", padding: "0.15rem 0.45rem", borderRadius: 4, fontWeight: 600, textTransform: "capitalize" as const },
  actionTag: { fontSize: "0.7rem", background: C.amberLight, color: C.amber, padding: "0.1rem 0.4rem", borderRadius: 3, fontWeight: 600 },
  topic: { margin: 0, fontWeight: 500, color: C.text, fontSize: "0.9rem" },
  meta: { display: "flex", gap: "0.75rem", alignItems: "center" },
  id: { fontFamily: F.mono, fontSize: "0.72rem", color: C.textMuted },
  score: { fontWeight: 700, fontSize: "0.82rem" },
  date: { fontSize: "0.78rem", color: C.textMuted, marginLeft: "auto" },
};
