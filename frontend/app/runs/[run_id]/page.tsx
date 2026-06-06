"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { api, getStreamUrl } from "../../../lib/api";
import { C, F, statusColor, statusBg } from "../../../lib/design";
import StatusTimeline from "../../../components/StatusTimeline";
import HITLPanel from "../../../components/HITLPanel";
import SourceList from "../../../components/SourceList";
import CodeViewer from "../../../components/CodeViewer";
import MarkdownViewer from "../../../components/MarkdownViewer";
import AgentTimeline from "../../../components/AgentTimeline";
import ReportView from "../../../components/ReportView";

interface Props { params: { run_id: string } }

type Tab = "activity" | "report" | "code" | "sources" | "evaluation" | "logs";

const ACTIVE = new Set(["discovering","researching","verifying_sources","analyzing","writing_report","planning_poc","generating_code","reviewing_code","evaluating","improving","publishing"]);
const AWAITING = new Set(["awaiting_topic_approval","awaiting_report_approval","awaiting_improvement_approval","awaiting_github_approval"]);

export default function RunDetail({ params }: Props) {
  const { run_id } = params;
  const [run, setRun] = useState<any>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<Tab>("activity");
  const esRef = useRef<EventSource | null>(null);

  const fetchOnce = async () => {
    try {
      const d = await api.getRun(run_id);
      setRun(d);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const manualRefresh = async () => {
    try {
      const d = await api.getRun(run_id);
      setRun(d);
    } catch { /* ignore */ }
  };

  useEffect(() => {
    fetchOnce();
    const es = new EventSource(getStreamUrl(run_id));
    esRef.current = es;
    es.onmessage = (evt) => {
      try {
        const data = JSON.parse(evt.data);
        setRun(data);
        setLoading(false);
      } catch { /* ignore */ }
    };
    es.addEventListener("done", () => { es.close(); setTimeout(manualRefresh, 800); });
    es.addEventListener("error", (evt: Event) => {
      try {
        const data = JSON.parse((evt as MessageEvent).data);
        if (data.detail) setError(data.detail);
      } catch { /* ignore */ }
      es.close();
    });
    return () => { es.close(); };
  }, [run_id]);

  if (loading) return <Loader />;
  if (error) return <ErrorView msg={error} />;
  if (!run) return null;

  const topic = run.approved_topic ?? run.selected_topic?.title ?? run.input_topic ?? "Auto-discover";
  const files = run.generated_files ?? [];
  const sources = run.verified_sources ?? run.report_json?.sources ?? [];
  const logs = run.agent_logs ?? [];
  const errors = run.errors ?? [];
  const isAwaiting = AWAITING.has(run.status);
  const isActive = ACTIVE.has(run.status);
  const isFailed = run.status === "failed";

  const totalTokens = logs.reduce((a: number, l: any) => a + (l.input_tokens ?? 0) + (l.output_tokens ?? 0), 0);
  const totalCost = logs.reduce((a: number, l: any) => a + (l.estimated_cost_usd ?? 0), 0);

  const tabs: { key: Tab; label: string; count?: number; urgent?: boolean }[] = [
    { key: "activity", label: "Activity", urgent: isAwaiting },
    { key: "report", label: "Report" },
    { key: "code", label: "Code", count: files.length },
    { key: "sources", label: "Sources", count: sources.length },
    { key: "evaluation", label: "Evaluation" },
    { key: "logs", label: "Logs", count: logs.length },
  ];

  const sc = statusColor(run.status);
  const sb = statusBg(run.status);

  return (
    <div>
      {/* HITL banner */}
      {isAwaiting && (
        <div style={styles.hitlBanner}>
          <div style={styles.hitlBannerLeft}>
            <span style={styles.hitlBannerDot} />
            <span style={styles.hitlBannerText}>
              Waiting for your approval — <strong>{run.status.replace(/_/g, " ")}</strong>
            </span>
          </div>
          <button onClick={() => setTab("activity")} style={styles.hitlBannerBtn}>
            Review &amp; Approve →
          </button>
        </div>
      )}

      {isActive && (
        <div style={styles.activeBanner}>
          <span style={styles.activeDot} />
          <span style={{ fontSize: "0.82rem", color: C.blue }}>
            Running: <strong>{run.status.replace(/_/g, " ")}</strong> — live
          </span>
        </div>
      )}

      {isFailed && (
        <div style={styles.failedBanner}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span style={{ fontSize: "0.85rem", color: C.red, fontWeight: 600 }}>
              Run failed
              {errors.length > 0 && ` — ${errors[errors.length - 1].slice(0, 120)}`}
            </span>
          </div>
          <button
            onClick={() => api.retryRun(run_id).then(manualRefresh)}
            style={styles.retryBtn}
          >
            ↺ Retry from last step
          </button>
        </div>
      )}

      {/* Header */}
      <div style={styles.header}>
        <div style={styles.breadcrumb}>
          <Link href="/runs" style={styles.breadLink}>Runs</Link>
          <span style={styles.breadSep}>/</span>
          <span style={styles.breadId}>{run_id.slice(0, 8)}</span>
        </div>
        <div style={styles.titleRow}>
          <h1 style={styles.title}>{topic}</h1>
          <div style={styles.titleActions}>
            <span style={{ ...styles.statusBadge, color: sc, background: sb }}>
              {run.status.replace(/_/g, " ")}
            </span>
            {run.eval_score != null && (
              <span style={{ ...styles.scoreBadge, color: run.eval_score >= 8 ? C.green : run.eval_score >= 7 ? C.amber : C.red }}>
                {run.eval_score.toFixed(1)}/10
              </span>
            )}
            <button onClick={manualRefresh} style={styles.iconBtn} title="Refresh">↻</button>
            {run.status === "failed" && (
              <button
                onClick={() => api.retryRun(run_id).then(manualRefresh)}
                style={{ ...styles.iconBtn, color: C.green, borderColor: C.green, fontWeight: 700 }}
                title="Retry from last failed step"
              >
                ↺ Retry
              </button>
            )}
            <button
              onClick={() => api.cancelRun(run_id).then(manualRefresh)}
              style={{ ...styles.iconBtn, color: C.red }}
              disabled={["complete", "failed"].includes(run.status)}
              title="Cancel run"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Meta strip */}
        <div style={styles.metaStrip}>
          <MetaItem label="Run ID" value={run_id.slice(0, 8)} mono />
          <MetaItem label="Tokens" value={totalTokens.toLocaleString()} />
          <MetaItem label="Cost" value={`$${totalCost.toFixed(4)}`} />
          {logs.length > 0 && <MetaItem label="Agents" value={logs.length} />}
          {run.github_repo_url && (
            <a href={run.github_repo_url} target="_blank" rel="noreferrer" style={styles.ghLink}>
              View on GitHub →
            </a>
          )}
        </div>
      </div>

      {/* Body: sidebar + content */}
      <div style={styles.body}>
        {/* Left sidebar */}
        <aside style={styles.sidebar}>
          <p style={styles.sideLabel}>Pipeline</p>
          <StatusTimeline status={run.status} />

          {isFailed && errors.length > 0 && (
            <div style={styles.sideErrors}>
              <p style={styles.sideLabel}>Errors</p>
              {errors.slice(0, 3).map((e: string, i: number) => (
                <p key={i} style={styles.sideError}>{e}</p>
              ))}
            </div>
          )}
        </aside>

        {/* Main content */}
        <div style={styles.main}>
          {/* Tabs */}
          <div style={styles.tabBar}>
            {tabs.map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                style={{
                  ...styles.tab,
                  ...(tab === t.key ? styles.tabActive : {}),
                  ...(t.urgent ? styles.tabUrgent : {}),
                }}
              >
                {t.label}
                {t.count != null && t.count > 0 && (
                  <span style={styles.tabCount}>{t.count}</span>
                )}
                {t.urgent && <span style={styles.urgentDot} />}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div style={styles.tabContent}>

            {/* Activity */}
            {tab === "activity" && (
              <div>
                {isAwaiting && (
                  <div style={styles.hitlBox}>
                    <HITLPanel
                      runId={run_id}
                      status={run.status}
                      topicApproved={run.topic_approved}
                      reportApproved={run.report_approved}
                      pocApproved={run.poc_approved}
                      githubPushApproved={run.github_push_approved}
                      selectedTopic={run.selected_topic}
                      discoveredTopics={run.discovered_topics ?? []}
                      run={run}
                      onAction={manualRefresh}
                    />
                  </div>
                )}
                <AgentTimeline logs={logs} run={run} />
              </div>
            )}

            {/* Report */}
            {tab === "report" && (
              <div>
                {run.report_json ? (
                  <ReportView report={run.report_json} />
                ) : run.report_markdown ? (
                  <MarkdownViewer content={run.report_markdown} />
                ) : (
                  <EmptyState msg="Report not generated yet." />
                )}
              </div>
            )}

            {/* Code */}
            {tab === "code" && (
              <div>
                {files.length > 0 ? (
                  <>
                    <CodeViewer files={files} />
                    {run.code_review && (
                      <div style={{ marginTop: "1rem" }}>
                        <p style={styles.sectionLabel}>Code Review</p>
                        <div style={{
                          ...styles.reviewBox,
                          borderColor: run.code_review.status === "approved" ? C.green : C.amber,
                        }}>
                          <span style={{ fontWeight: 700, fontSize: "0.82rem", color: run.code_review.status === "approved" ? C.green : C.amber }}>
                            {run.code_review.status?.toUpperCase()}
                          </span>
                          {(run.code_review.issues ?? []).map((iss: string, i: number) => (
                            <p key={i} style={{ margin: "0.2rem 0 0", fontSize: "0.82rem", color: C.amber }}>• {iss}</p>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <EmptyState msg="Code not generated yet." />
                )}
              </div>
            )}

            {/* Sources */}
            {tab === "sources" && (
              sources.length > 0
                ? <SourceList sources={sources} />
                : <EmptyState msg="No verified sources yet." />
            )}

            {/* Evaluation */}
            {tab === "evaluation" && (
              <div>
                {run.evaluation ? (
                  <EvalPanel evaluation={run.evaluation} score={run.eval_score} flags={run.eval_flags} />
                ) : (
                  <EmptyState msg="Evaluation not complete yet." />
                )}
              </div>
            )}

            {/* Logs */}
            {tab === "logs" && (
              <div>
                {logs.length === 0 ? (
                  <EmptyState msg="No agent logs yet." />
                ) : (
                  <>
                    <table style={styles.logTable}>
                      <thead>
                        <tr>
                          {["Agent","Status","Latency","Tokens","Cost","Model"].map((h) => (
                            <th key={h} style={styles.th}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {logs.map((l: any, i: number) => (
                          <tr key={i} style={{ background: i % 2 === 0 ? C.bg : C.bgSubtle }}>
                            <td style={styles.td}>{l.agent_name}</td>
                            <td style={{ ...styles.td, color: l.status === "success" ? C.green : l.status === "error" ? C.red : C.textSec }}>{l.status}</td>
                            <td style={{ ...styles.td, fontFamily: F.mono }}>{l.latency_ms}ms</td>
                            <td style={{ ...styles.td, fontFamily: F.mono }}>{((l.input_tokens ?? 0) + (l.output_tokens ?? 0)).toLocaleString()}</td>
                            <td style={{ ...styles.td, fontFamily: F.mono }}>${(l.estimated_cost_usd ?? 0).toFixed(4)}</td>
                            <td style={{ ...styles.td, fontFamily: F.mono, color: C.textMuted }}>{l.model_name ?? "—"}</td>
                          </tr>
                        ))}
                        <tr style={{ background: C.greenLight }}>
                          <td style={{ ...styles.td, fontWeight: 700 }} colSpan={2}>Total</td>
                          <td style={styles.td} />
                          <td style={{ ...styles.td, fontFamily: F.mono, fontWeight: 700 }}>{totalTokens.toLocaleString()}</td>
                          <td style={{ ...styles.td, fontFamily: F.mono, fontWeight: 700 }}>${totalCost.toFixed(4)}</td>
                          <td style={styles.td} />
                        </tr>
                      </tbody>
                    </table>
                    {errors.length > 0 && (
                      <div style={{ marginTop: "1rem" }}>
                        <p style={styles.sectionLabel}>Errors</p>
                        {errors.map((e: string, i: number) => (
                          <p key={i} style={{ margin: "0.2rem 0", fontSize: "0.82rem", color: C.red }}>• {e}</p>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

function EvalPanel({ evaluation, score, flags }: { evaluation: any; score?: number; flags?: string[] }) {
  const dim = evaluation?.dimension_scores ?? {};
  const allFlags = flags ?? evaluation?.flags ?? [];
  const improvements = evaluation?.improvements ?? [];

  return (
    <div>
      {score != null && (
        <div style={evalStyles.scoreCard}>
          <div style={evalStyles.bigScore}>
            <span style={{ ...evalStyles.scoreNum, color: score >= 8 ? C.green : score >= 7 ? C.amber : C.red }}>
              {score.toFixed(1)}
            </span>
            <span style={evalStyles.scoreDenom}>/10</span>
          </div>
          <span style={{ ...evalStyles.passBadge, background: evaluation.passed ? C.greenLight : C.redLight, color: evaluation.passed ? C.green : C.red }}>
            {evaluation.passed ? "Passed" : "Failed"}
          </span>
        </div>
      )}

      {Object.keys(dim).length > 0 && (
        <div style={evalStyles.dimGrid}>
          {Object.entries(dim).map(([k, v]) => (
            <div key={k} style={evalStyles.dimCard}>
              <p style={evalStyles.dimLabel}>{k.replace(/_/g, " ")}</p>
              <p style={{ ...evalStyles.dimScore, color: (v as number) >= 8 ? C.green : (v as number) >= 6 ? C.amber : C.red }}>
                {v as number}/10
              </p>
            </div>
          ))}
        </div>
      )}

      {allFlags.length > 0 && (
        <div style={{ marginTop: "0.75rem" }}>
          <p style={styles.sectionLabel}>Flags</p>
          {allFlags.map((f: string, i: number) => (
            <p key={i} style={{ margin: "0.2rem 0", fontSize: "0.82rem", color: C.amber }}>⚠ {f}</p>
          ))}
        </div>
      )}

      {improvements.length > 0 && (
        <div style={{ marginTop: "0.75rem" }}>
          <p style={styles.sectionLabel}>Improvements</p>
          {improvements.map((imp: string, i: number) => (
            <p key={i} style={{ margin: "0.2rem 0", fontSize: "0.82rem", color: C.textSec }}>→ {imp}</p>
          ))}
        </div>
      )}
    </div>
  );
}

function MetaItem({ label, value, mono }: { label: string; value: string | number; mono?: boolean }) {
  return (
    <div style={{ display: "flex", gap: "0.35rem", alignItems: "baseline" }}>
      <span style={{ fontSize: "0.72rem", color: C.textMuted }}>{label}</span>
      <span style={{ fontSize: "0.82rem", color: C.textSec, fontFamily: mono ? F.mono : F.sans, fontWeight: 500 }}>{value}</span>
    </div>
  );
}

function EmptyState({ msg }: { msg: string }) {
  return (
    <div style={{ padding: "2rem", textAlign: "center", color: C.textMuted, fontSize: "0.85rem" }}>
      {msg}
    </div>
  );
}

function Loader() {
  return (
    <div style={{ padding: "3rem", textAlign: "center", color: C.textMuted, fontSize: "0.85rem" }}>
      Loading run…
    </div>
  );
}

function ErrorView({ msg }: { msg: string }) {
  return (
    <div style={{ padding: "2rem", color: C.red, fontSize: "0.9rem" }}>{msg}</div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  hitlBanner: { display: "flex", justifyContent: "space-between", alignItems: "center", background: C.amberLight, border: `1px solid ${C.amber}44`, borderRadius: 7, padding: "0.65rem 1rem", marginBottom: "1rem", gap: "1rem", flexWrap: "wrap" },
  hitlBannerLeft: { display: "flex", alignItems: "center", gap: "0.5rem" },
  hitlBannerDot: { width: 8, height: 8, borderRadius: "50%", background: C.amber, flexShrink: 0 },
  hitlBannerText: { fontSize: "0.85rem", color: C.text },
  hitlBannerBtn: { padding: "0.4rem 0.9rem", background: C.amber, color: "#fff", border: "none", borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.82rem", fontFamily: F.sans, flexShrink: 0 },
  activeBanner: { display: "flex", alignItems: "center", gap: "0.5rem", background: C.blueLight, border: `1px solid ${C.blue}33`, borderRadius: 7, padding: "0.5rem 0.85rem", marginBottom: "1rem" },
  activeDot: { width: 7, height: 7, borderRadius: "50%", background: C.blue, flexShrink: 0 },
  failedBanner: { display: "flex", justifyContent: "space-between", alignItems: "center", background: C.redLight, border: `1px solid ${C.red}44`, borderRadius: 7, padding: "0.65rem 1rem", marginBottom: "1rem", gap: "1rem", flexWrap: "wrap" as const },
  retryBtn: { padding: "0.4rem 0.9rem", background: C.green, color: "#fff", border: "none", borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.82rem", fontFamily: F.sans, flexShrink: 0 },
  header: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "1.1rem 1.25rem", marginBottom: "1rem" },
  breadcrumb: { display: "flex", alignItems: "center", gap: "0.3rem", marginBottom: "0.5rem" },
  breadLink: { fontSize: "0.8rem", color: C.blue, textDecoration: "none" },
  breadSep: { fontSize: "0.8rem", color: C.textMuted },
  breadId: { fontSize: "0.8rem", color: C.textMuted, fontFamily: F.mono },
  titleRow: { display: "flex", alignItems: "flex-start", gap: "0.75rem", flexWrap: "wrap", marginBottom: "0.75rem" },
  title: { margin: 0, fontSize: "1.25rem", fontWeight: 700, color: C.text, flex: 1, lineHeight: 1.3 },
  titleActions: { display: "flex", alignItems: "center", gap: "0.4rem", flexShrink: 0 },
  statusBadge: { fontSize: "0.75rem", padding: "0.2rem 0.55rem", borderRadius: 4, fontWeight: 600, textTransform: "capitalize" as const },
  scoreBadge: { fontWeight: 700, fontSize: "0.9rem" },
  iconBtn: { background: "none", border: `1px solid ${C.border}`, borderRadius: 4, cursor: "pointer", padding: "0.2rem 0.45rem", fontSize: "0.85rem", color: C.textSec, fontFamily: F.mono },
  metaStrip: { display: "flex", gap: "1.25rem", flexWrap: "wrap", alignItems: "center" },
  ghLink: { fontSize: "0.82rem", color: C.green, textDecoration: "none", fontWeight: 600, marginLeft: "auto" },
  body: { display: "flex", gap: "1rem", alignItems: "flex-start" },
  sidebar: { width: 200, flexShrink: 0, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "0.9rem 0.85rem", position: "sticky" as const, top: 72 },
  sideLabel: { margin: "0 0 0.5rem", fontSize: "0.7rem", color: C.textMuted, fontWeight: 700, textTransform: "uppercase" as const, letterSpacing: "0.06em" },
  sideErrors: { marginTop: "1rem" },
  sideError: { margin: "0.2rem 0", fontSize: "0.75rem", color: C.red },
  main: { flex: 1, minWidth: 0 },
  tabBar: { display: "flex", gap: "0.15rem", borderBottom: `1px solid ${C.border}`, marginBottom: "1rem", flexWrap: "wrap" },
  tab: { padding: "0.5rem 0.85rem", border: "none", background: "transparent", cursor: "pointer", fontFamily: F.sans, fontSize: "0.82rem", color: C.textSec, borderBottom: "2px solid transparent", display: "flex", alignItems: "center", gap: "0.3rem", whiteSpace: "nowrap" as const },
  tabActive: { color: C.text, fontWeight: 600, borderBottom: `2px solid ${C.blue}` },
  tabUrgent: { color: C.amber },
  tabCount: { fontSize: "0.68rem", background: C.bgMuted, color: C.textMuted, padding: "0.05rem 0.35rem", borderRadius: 10, fontWeight: 600 },
  urgentDot: { width: 6, height: 6, borderRadius: "50%", background: C.amber, display: "inline-block" },
  tabContent: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "1.1rem" },
  hitlBox: { marginBottom: "1.25rem" },
  sectionLabel: { margin: "0 0 0.4rem", fontSize: "0.72rem", color: C.textMuted, fontWeight: 700, textTransform: "uppercase" as const, letterSpacing: "0.05em" },
  reviewBox: { border: "1px solid", borderRadius: 6, padding: "0.65rem 0.75rem" },
  rawJson: { margin: 0, fontSize: "0.75rem", background: "#0D1117", color: "#E6EDF3", padding: "1rem", borderRadius: 6, overflow: "auto", maxHeight: 500, fontFamily: F.mono },
  logTable: { width: "100%", borderCollapse: "collapse" as const, fontSize: "0.8rem" },
  th: { textAlign: "left" as const, padding: "0.4rem 0.75rem", fontSize: "0.72rem", color: C.textMuted, fontWeight: 700, textTransform: "uppercase" as const, letterSpacing: "0.05em", borderBottom: `1px solid ${C.border}` },
  td: { padding: "0.45rem 0.75rem", borderBottom: `1px solid ${C.border}`, color: C.textSec },
};

const evalStyles: Record<string, React.CSSProperties> = {
  scoreCard: { display: "flex", alignItems: "center", gap: "1rem", padding: "0.75rem 1rem", background: C.bgSubtle, borderRadius: 8, marginBottom: "1rem", border: `1px solid ${C.border}` },
  bigScore: { display: "flex", alignItems: "baseline", gap: "0.15rem" },
  scoreNum: { fontSize: "2rem", fontWeight: 800 },
  scoreDenom: { fontSize: "1rem", color: C.textMuted },
  passBadge: { fontSize: "0.8rem", fontWeight: 700, padding: "0.2rem 0.6rem", borderRadius: 5 },
  dimGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px, 1fr))", gap: "0.5rem" },
  dimCard: { background: C.bgSubtle, border: `1px solid ${C.border}`, borderRadius: 6, padding: "0.5rem 0.65rem" },
  dimLabel: { margin: "0 0 0.15rem", fontSize: "0.7rem", color: C.textMuted, textTransform: "capitalize" as const },
  dimScore: { margin: 0, fontWeight: 700, fontSize: "1.1rem" },
};
