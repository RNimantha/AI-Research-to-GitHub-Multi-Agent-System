"use client";
import { useState } from "react";
import { api } from "../lib/api";
import { C, F } from "../lib/design";

interface DiscoveredTopic {
  title: string;
  summary?: string;
  source_urls?: string[];
  novelty_score?: number;
  poc_feasibility_score?: number;
  business_value_score?: number;
}

interface Props {
  runId: string;
  status: string;
  topicApproved: boolean;
  reportApproved: boolean;
  pocApproved: boolean;
  githubPushApproved: boolean;
  selectedTopic: any;
  discoveredTopics: DiscoveredTopic[];
  run?: any;
  onAction: () => void;
}

export default function HITLPanel({
  runId, status, topicApproved, reportApproved, pocApproved, githubPushApproved,
  selectedTopic, discoveredTopics, run, onAction,
}: Props) {
  const [msg, setMsg] = useState("");
  const [loading, setLoading] = useState(false);
  const [chosenTitle, setChosenTitle] = useState(selectedTopic?.title ?? "");
  const [customTitle, setCustomTitle] = useState("");
  const [revisionNotes, setRevisionNotes] = useState("");

  const act = async (fn: () => Promise<any>, label: string) => {
    setLoading(true);
    setMsg("");
    try {
      await fn();
      setMsg(`${label} submitted`);
      setRevisionNotes("");
      setTimeout(onAction, 1200);
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (status === "complete") {
    return (
      <div style={styles.allPassed}>
        <span style={styles.checkmark}>✓</span>
        <span style={{ fontSize: "0.85rem", color: C.green, fontWeight: 600 }}>All gates passed</span>
      </div>
    );
  }

  // Gate 1
  if (status === "awaiting_topic_approval") {
    const finalTitle = customTitle.trim() || chosenTitle || selectedTopic?.title;
    return (
      <div style={styles.gate}>
        <GateHeader num={1} title="Topic Approval" />
        <p style={styles.gateDesc}>
          Review the AI-selected topic or choose a different one from the list below.
        </p>

        {selectedTopic && (
          <div style={styles.aiPickBox}>
            <span style={styles.aiTag}>AI selected</span>
            <p style={styles.aiPickTitle}>{selectedTopic.title}</p>
            {selectedTopic.reason && <p style={styles.aiPickReason}>{selectedTopic.reason}</p>}
            {selectedTopic.difficulty && (
              <p style={styles.aiPickMeta}>Difficulty: {selectedTopic.difficulty}</p>
            )}
          </div>
        )}

        {discoveredTopics.length > 1 && (
          <div style={styles.topicsSection}>
            <p style={styles.topicsLabel}>All discovered topics</p>
            {discoveredTopics.map((t, i) => {
              const sel = chosenTitle === t.title || (!chosenTitle && t.title === selectedTopic?.title);
              return (
                <div
                  key={i}
                  onClick={() => { setChosenTitle(t.title); setCustomTitle(""); }}
                  style={{ ...styles.topicRow, ...(sel ? styles.topicRowSel : {}) }}
                >
                  <div style={styles.topicRowDot}>
                    {sel ? <span style={styles.selDot} /> : <span style={styles.unselDot} />}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={styles.topicRowTitle}>{t.title}</p>
                    <div style={{ display: "flex", gap: "0.75rem" }}>
                      {t.novelty_score != null && <ScoreLabel label="N" value={t.novelty_score} />}
                      {t.poc_feasibility_score != null && <ScoreLabel label="POC" value={t.poc_feasibility_score} />}
                      {t.business_value_score != null && <ScoreLabel label="Biz" value={t.business_value_score} />}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        <div style={styles.orRow}><span style={styles.orLine} /><span style={styles.orText}>or</span><span style={styles.orLine} /></div>
        <input
          type="text"
          value={customTitle}
          onChange={(e) => setCustomTitle(e.target.value)}
          placeholder="Type a custom topic…"
          style={styles.input}
        />
        {finalTitle && (
          <p style={styles.approving}>Will approve: <strong>{finalTitle}</strong></p>
        )}
        <Actions
          loading={loading}
          onApprove={() => act(() => api.approveTopic(runId, true, finalTitle), "Topic approved")}
          onReject={() => act(() => api.approveTopic(runId, false), "Topic rejected")}
          approveLabel="Approve Topic"
          disabled={!finalTitle}
        />
        {msg && <p style={styles.msg}>{msg}</p>}
      </div>
    );
  }

  // Gate 2 — shown only when backend is actually waiting
  if (status === "awaiting_report_approval") {
    return (
      <div style={styles.gate}>
        <GateHeader num={2} title="Report Approval" />
        <p style={styles.gateDesc}>Review the Report tab. Add revision notes to request changes.</p>
        <textarea
          value={revisionNotes}
          onChange={(e) => setRevisionNotes(e.target.value)}
          placeholder="Revision notes (leave blank to approve as-is)"
          style={styles.textarea}
        />
        <Actions
          loading={loading}
          onApprove={() => act(() => api.approveReport(runId, true), "Report approved")}
          onRevise={revisionNotes.trim() ? () => act(() => api.approveReport(runId, false, revisionNotes), "Revision requested") : undefined}
          approveLabel="Approve Report"
        />
        {msg && <p style={styles.msg}>{msg}</p>}
      </div>
    );
  }

  // Gate 3 — Improvement approval
  if (status === "awaiting_improvement_approval") {
    const improvements: string[] = run?.evaluation?.improvements ?? [];
    const flags: string[] = run?.eval_flags ?? [];
    const dimScores: Record<string, number> = run?.evaluation?.dimension_scores ?? {};
    const weakDims = Object.entries(dimScores).filter(([, v]) => (v as number) < 8);

    return (
      <div style={styles.gate}>
        <GateHeader num={3} title="Improvement Suggestions" />
        <p style={styles.gateDesc}>
          Evaluation passed (score: <strong>{run?.eval_score?.toFixed(1)}</strong>/10).
          The evaluator found areas to improve. Apply them to get a better report before publishing.
        </p>

        {weakDims.length > 0 && (
          <div style={{ marginBottom: "0.75rem" }}>
            <p style={styles.sectionLabel}>Weak dimensions</p>
            <div style={{ display: "flex", gap: "0.35rem", flexWrap: "wrap" }}>
              {weakDims.map(([k, v]) => (
                <span key={k} style={{ fontSize: "0.75rem", background: C.amberLight, color: C.amber, padding: "0.15rem 0.45rem", borderRadius: 4, fontWeight: 600 }}>
                  {k.replace(/_/g, " ")}: {v}/10
                </span>
              ))}
            </div>
          </div>
        )}

        {improvements.length > 0 && (
          <div style={{ marginBottom: "0.75rem" }}>
            <p style={styles.sectionLabel}>Suggested improvements</p>
            <ul style={{ margin: 0, paddingLeft: "1.25rem" }}>
              {improvements.map((imp: string, i: number) => (
                <li key={i} style={{ fontSize: "0.84rem", color: C.textSec, lineHeight: 1.6, marginBottom: "0.2rem" }}>
                  {imp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {flags.length > 0 && (
          <div style={{ marginBottom: "0.75rem" }}>
            <p style={styles.sectionLabel}>Flags</p>
            {flags.map((f: string, i: number) => (
              <p key={i} style={{ margin: "0.15rem 0", fontSize: "0.82rem", color: C.amber }}>⚑ {f}</p>
            ))}
          </div>
        )}

        <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem", flexWrap: "wrap" }}>
          <button
            disabled={loading}
            onClick={() => act(() => api.approveImprovements(runId, true), "Applying improvements…")}
            style={{ padding: "0.5rem 1rem", background: C.blue, color: "#fff", border: "none", borderRadius: 5, cursor: "pointer", fontWeight: 700, fontSize: "0.85rem", fontFamily: F.sans }}
          >
            Apply improvements
          </button>
          <button
            disabled={loading}
            onClick={() => act(() => api.approveImprovements(runId, false), "Skipped improvements")}
            style={{ padding: "0.5rem 1rem", background: C.bgMuted, color: C.textSec, border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans }}
          >
            Skip — publish as-is
          </button>
        </div>
        {msg && <p style={styles.msg}>{msg}</p>}
      </div>
    );
  }

  // Gate 4 — GitHub push (Gate 3 / POC approval is handled by auto code-review in backend)
  if (status === "awaiting_github_approval") {
    return (
      <div style={styles.gate}>
        <GateHeader num={4} title="GitHub Publish" />
        <p style={styles.gateDesc}>
          Evaluation passed. Review the Report and Code tabs, then publish to GitHub. This cannot be undone.
        </p>
        <div style={styles.publishRow}>
          <button
            disabled={loading}
            onClick={() => act(() => api.approveGithubPush(runId, true), "GitHub push approved")}
            style={styles.publishBtn}
          >
            Publish to GitHub
          </button>
          <button
            disabled={loading}
            onClick={() => act(() => api.approveGithubPush(runId, false), "GitHub push held")}
            style={styles.holdBtn}
          >
            Hold
          </button>
        </div>
        {msg && <p style={styles.msg}>{msg}</p>}
      </div>
    );
  }

  return null;
}

function GateHeader({ num, title }: { num: number; title: string }) {
  return (
    <div style={gateHeaderStyles.row}>
      <span style={gateHeaderStyles.num}>{num}</span>
      <span style={gateHeaderStyles.title}>{title}</span>
      <span style={gateHeaderStyles.badge}>Action required</span>
    </div>
  );
}

function Actions({ loading, onApprove, onReject, onRevise, approveLabel, disabled }: {
  loading: boolean;
  onApprove: () => void;
  onReject?: () => void;
  onRevise?: () => void;
  approveLabel: string;
  disabled?: boolean;
}) {
  return (
    <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginTop: "0.75rem" }}>
      <button
        disabled={loading || disabled}
        onClick={onApprove}
        style={actionStyles.approve}
      >
        {approveLabel}
      </button>
      {onRevise && (
        <button disabled={loading} onClick={onRevise} style={actionStyles.revise}>
          Request Revision
        </button>
      )}
      {onReject && (
        <button disabled={loading} onClick={onReject} style={actionStyles.reject}>
          Reject
        </button>
      )}
    </div>
  );
}

function ScoreLabel({ label, value }: { label: string; value: number }) {
  const color = value >= 8 ? C.green : value >= 6 ? C.amber : C.red;
  return <span style={{ fontSize: "0.72rem", color, fontWeight: 600 }}>{label}: {value}</span>;
}

const styles: Record<string, React.CSSProperties> = {
  gate: { background: C.bg, border: `2px solid ${C.amber}`, borderRadius: 8, padding: "1.1rem", marginBottom: "0.75rem" },
  gateDesc: { margin: "0.4rem 0 0.75rem", fontSize: "0.83rem", color: C.textSec },
  sectionLabel: { margin: "0 0 0.35rem", fontSize: "0.7rem", fontWeight: 700, color: C.textMuted, textTransform: "uppercase" as const, letterSpacing: "0.06em" },
  aiPickBox: { background: C.blueLight, border: `1px solid ${C.blue}33`, borderRadius: 6, padding: "0.75rem", marginBottom: "0.75rem" },
  aiTag: { fontSize: "0.68rem", background: C.blue, color: "#fff", padding: "0.1rem 0.35rem", borderRadius: 3, fontWeight: 700 },
  aiPickTitle: { margin: "0.35rem 0 0.25rem", fontWeight: 700, fontSize: "0.9rem", color: C.text },
  aiPickReason: { margin: "0 0 0.3rem", fontSize: "0.8rem", color: C.textSec, lineHeight: 1.5 },
  aiPickMeta: { margin: 0, fontSize: "0.75rem", color: C.textMuted },
  topicsSection: { marginBottom: "0.5rem" },
  topicsLabel: { margin: "0 0 0.4rem", fontSize: "0.72rem", color: C.textMuted, fontWeight: 700, textTransform: "uppercase" as const, letterSpacing: "0.05em" },
  topicRow: { display: "flex", gap: "0.5rem", alignItems: "flex-start", padding: "0.5rem 0.6rem", borderRadius: 5, cursor: "pointer", marginBottom: "0.25rem", border: `1px solid ${C.border}`, background: C.bgSubtle },
  topicRowSel: { border: `1px solid ${C.blue}`, background: C.blueLight },
  topicRowDot: { paddingTop: "0.2rem", flexShrink: 0 },
  selDot: { display: "block", width: 10, height: 10, borderRadius: "50%", background: C.blue, border: `2px solid ${C.blue}` },
  unselDot: { display: "block", width: 10, height: 10, borderRadius: "50%", background: C.bg, border: `2px solid ${C.border}` },
  topicRowTitle: { margin: "0 0 0.2rem", fontWeight: 500, fontSize: "0.83rem", color: C.text },
  orRow: { display: "flex", alignItems: "center", gap: "0.5rem", margin: "0.5rem 0" },
  orLine: { flex: 1, height: 1, background: C.border, display: "block" },
  orText: { fontSize: "0.75rem", color: C.textMuted, flexShrink: 0 },
  input: { width: "100%", padding: "0.55rem 0.7rem", border: `1px solid ${C.border}`, borderRadius: 5, fontFamily: F.sans, fontSize: "0.85rem", color: C.text, background: C.bg, boxSizing: "border-box" as const, outline: "none" },
  approving: { margin: "0.4rem 0 0", fontSize: "0.8rem", color: C.textSec },
  textarea: { width: "100%", padding: "0.55rem 0.7rem", border: `1px solid ${C.border}`, borderRadius: 5, fontFamily: F.sans, fontSize: "0.85rem", color: C.text, background: C.bg, boxSizing: "border-box" as const, minHeight: 70, resize: "vertical" as const, outline: "none" },
  msg: { margin: "0.5rem 0 0", fontSize: "0.8rem", color: C.green },
  allPassed: { display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.6rem 0.75rem", background: C.greenLight, borderRadius: 6 },
  checkmark: { fontSize: "0.9rem", color: C.green },
  publishRow: { display: "flex", gap: "0.5rem" },
  publishBtn: { padding: "0.6rem 1.25rem", background: C.blue, color: "#fff", border: "none", borderRadius: 6, cursor: "pointer", fontWeight: 700, fontSize: "0.9rem", fontFamily: F.sans },
  holdBtn: { padding: "0.6rem 0.9rem", background: C.bg, color: C.textSec, border: `1px solid ${C.border}`, borderRadius: 6, cursor: "pointer", fontSize: "0.9rem", fontFamily: F.sans },
};

const gateHeaderStyles: Record<string, React.CSSProperties> = {
  row: { display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" },
  num: { width: 20, height: 20, borderRadius: "50%", background: C.amber, color: "#fff", fontSize: "0.7rem", fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 },
  title: { fontWeight: 700, fontSize: "0.9rem", color: C.text, flex: 1 },
  badge: { fontSize: "0.68rem", background: C.amber, color: "#fff", padding: "0.1rem 0.4rem", borderRadius: 3, fontWeight: 700, flexShrink: 0 },
};

const actionStyles: Record<string, React.CSSProperties> = {
  approve: { padding: "0.5rem 1rem", background: C.green, color: "#fff", border: "none", borderRadius: 6, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  revise: { padding: "0.5rem 0.9rem", background: C.bg, color: C.amber, border: `1px solid ${C.amber}`, borderRadius: 6, cursor: "pointer", fontSize: "0.85rem", fontFamily: F.sans },
  reject: { padding: "0.5rem 0.9rem", background: C.bg, color: C.red, border: `1px solid ${C.red}`, borderRadius: 6, cursor: "pointer", fontSize: "0.85rem", fontFamily: F.sans },
};
