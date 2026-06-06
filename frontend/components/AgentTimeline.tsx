"use client";
import { useState } from "react";
import { C, F } from "../lib/design";

interface AgentLog {
  agent_name: string;
  status: string;
  input_tokens?: number;
  output_tokens?: number;
  estimated_cost_usd?: number;
  latency_ms?: number;
  model_name?: string;
  error_message?: string;
  input_json?: any;
  output_json?: any;
}

interface DiscoveredTopic {
  title: string;
  summary?: string;
  novelty_score?: number;
  poc_feasibility_score?: number;
  business_value_score?: number;
}

interface Props {
  logs: AgentLog[];
  run: any;
}

export default function AgentTimeline({ logs, run }: Props) {
  const discoveredTopics: DiscoveredTopic[] = run.discovered_topics ?? [];
  const selectedTopic = run.selected_topic;
  const researchContext = run.research_context;
  const technicalAnalysis = run.technical_analysis;
  const pocPlan = run.poc_plan;

  if (logs.length === 0 && discoveredTopics.length === 0) {
    return (
      <div style={styles.empty}>
        <p style={{ margin: 0, color: C.textMuted, fontSize: "0.85rem" }}>
          No agent activity yet. The pipeline will appear here as it runs.
        </p>
      </div>
    );
  }

  return (
    <div style={styles.timeline}>
      {/* Discovery output */}
      {discoveredTopics.length > 0 && (
        <OutputBlock
          agent="Discovery Agent"
          status="complete"
          summary={`Found ${discoveredTopics.length} trending topics`}
          log={logs.find((l) => l.agent_name.toLowerCase().includes("discovery"))}
        >
          <div style={styles.topicGrid}>
            {discoveredTopics.map((t, i) => (
              <div key={i} style={{
                ...styles.topicCard,
                ...(selectedTopic?.title === t.title ? styles.topicCardSelected : {}),
              }}>
                {selectedTopic?.title === t.title && (
                  <span style={styles.aiSelectedTag}>AI selected</span>
                )}
                <p style={styles.topicCardTitle}>{t.title}</p>
                {t.summary && <p style={styles.topicCardSummary}>{t.summary}</p>}
                <div style={styles.scoreRow}>
                  {t.novelty_score != null && <Score label="Novelty" value={t.novelty_score} />}
                  {t.poc_feasibility_score != null && <Score label="POC" value={t.poc_feasibility_score} />}
                  {t.business_value_score != null && <Score label="Business" value={t.business_value_score} />}
                </div>
              </div>
            ))}
          </div>
        </OutputBlock>
      )}

      {/* Topic selection output */}
      {selectedTopic && (
        <OutputBlock
          agent="Topic Selection Agent"
          status="complete"
          summary={`Selected: "${selectedTopic.title}"`}
          log={logs.find((l) => l.agent_name.toLowerCase().includes("topic_selection") || l.agent_name.toLowerCase().includes("topic selection"))}
        >
          <div style={styles.selectedTopicBox}>
            <p style={styles.selectedTopicTitle}>{selectedTopic.title}</p>
            {selectedTopic.reason && <p style={styles.selectedTopicReason}>{selectedTopic.reason}</p>}
            <div style={styles.chipRow}>
              {selectedTopic.difficulty && <Chip label={`Difficulty: ${selectedTopic.difficulty}`} />}
            </div>
            {selectedTopic.expected_poc && (
              <p style={styles.pocExpected}><strong>Expected POC:</strong> {selectedTopic.expected_poc}</p>
            )}
          </div>
        </OutputBlock>
      )}

      {/* Research context */}
      {researchContext && (
        <OutputBlock
          agent="Research Agent"
          status="complete"
          summary="Research notes compiled"
          log={logs.find((l) => l.agent_name.toLowerCase().includes("research"))}
        >
          <ObjectOrText value={researchContext} />
        </OutputBlock>
      )}

      {/* Technical analysis */}
      {technicalAnalysis && (
        <OutputBlock
          agent="Technical Analysis Agent"
          status="complete"
          summary="Technical analysis complete"
          log={logs.find((l) => l.agent_name.toLowerCase().includes("technical"))}
        >
          <ObjectOrText value={technicalAnalysis} />
        </OutputBlock>
      )}

      {/* POC plan */}
      {pocPlan && (
        <OutputBlock
          agent="POC Planner Agent"
          status="complete"
          summary={`POC plan: ${pocPlan.project_name ?? "unnamed"}`}
          log={logs.find((l) => l.agent_name.toLowerCase().includes("planner"))}
        >
          <div style={styles.pocPlanBox}>
            {pocPlan.goal && <p style={styles.pocGoal}>{pocPlan.goal}</p>}
            {pocPlan.dependencies?.length > 0 && (
              <div style={styles.depsRow}>
                {pocPlan.dependencies.map((d: string) => <Chip key={d} label={d} mono />)}
              </div>
            )}
            {pocPlan.files?.length > 0 && (
              <div style={{ marginTop: "0.5rem" }}>
                <p style={styles.fileListLabel}>Files ({pocPlan.files.length})</p>
                {pocPlan.files.map((f: any, i: number) => (
                  <div key={i} style={styles.fileRow}>
                    <span style={styles.filePath}>{f.path}</span>
                    {f.purpose && <span style={styles.filePurpose}>{f.purpose}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        </OutputBlock>
      )}

      {/* Code review */}
      {run.code_review && (
        <OutputBlock
          agent="Code Reviewer Agent"
          status={run.code_review.status === "approved" ? "complete" : "error"}
          summary={run.code_review.status === "approved" ? "Code approved" : `${run.code_review.issues?.length ?? 0} issues found`}
          log={logs.find((l) => l.agent_name.toLowerCase().includes("reviewer") || l.agent_name.toLowerCase().includes("code_review"))}
        >
          <div style={{ ...styles.reviewBox, borderColor: run.code_review.status === "approved" ? C.green : C.amber }}>
            <p style={{ margin: "0 0 0.35rem", fontWeight: 600, color: run.code_review.status === "approved" ? C.green : C.amber }}>
              {run.code_review.status?.toUpperCase()}
            </p>
            {(run.code_review.issues ?? []).map((iss: string, i: number) => (
              <p key={i} style={{ margin: "0.15rem 0", color: C.amber, fontSize: "0.82rem" }}>• {iss}</p>
            ))}
          </div>
        </OutputBlock>
      )}

      {/* Evaluation */}
      {run.evaluation && (
        <OutputBlock
          agent="Evaluator Agent"
          status="complete"
          summary={`Score: ${run.eval_score?.toFixed(1) ?? "—"}/10 — ${run.evaluation.passed ? "Passed" : "Failed"}`}
          log={logs.find((l) => l.agent_name.toLowerCase().includes("eval"))}
        >
          <EvalOutput evaluation={run.evaluation} evalScore={run.eval_score} evalFlags={run.eval_flags} />
        </OutputBlock>
      )}

      {/* Other logs that don't have structured output */}
      {logs.filter((l) => {
        const n = l.agent_name.toLowerCase();
        const covered = ["discovery", "topic_selection", "topic selection", "research", "technical", "planner", "reviewer", "code_review", "eval"];
        return !covered.some((c) => n.includes(c));
      }).map((log, i) => (
        <OutputBlock
          key={i}
          agent={log.agent_name}
          status={log.status}
          summary={log.error_message ?? (log.status === "success" ? "Complete" : log.status)}
          log={log}
        >
          {log.output_json && (
            <pre style={styles.rawJson}>{JSON.stringify(log.output_json, null, 2)}</pre>
          )}
        </OutputBlock>
      ))}
    </div>
  );
}

function OutputBlock({
  agent, status, summary, log, children,
}: {
  agent: string;
  status: string;
  summary: string;
  log?: AgentLog;
  children?: React.ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const isError = status === "error" || status === "failed";
  const isComplete = status === "complete" || status === "success";

  return (
    <div style={blockStyles.wrapper}>
      <div style={blockStyles.track}>
        <div style={{
          ...blockStyles.dot,
          background: isError ? C.red : isComplete ? C.green : C.blue,
        }} />
        {<div style={blockStyles.line} />}
      </div>
      <div style={blockStyles.content}>
        <div style={blockStyles.header} onClick={() => setOpen(!open)}>
          <div style={blockStyles.headerLeft}>
            <span style={blockStyles.agentName}>{agent}</span>
            <span style={{ ...blockStyles.statusDot, color: isError ? C.red : isComplete ? C.green : C.blue }}>
              {isError ? "✗" : isComplete ? "✓" : "→"}
            </span>
            <span style={blockStyles.summary}>{summary}</span>
          </div>
          <div style={blockStyles.headerRight}>
            {log && (
              <>
                {log.latency_ms != null && <Meta value={`${log.latency_ms}ms`} />}
                {log.input_tokens != null && <Meta value={`${(log.input_tokens + (log.output_tokens ?? 0)).toLocaleString()} tok`} />}
                {log.estimated_cost_usd != null && <Meta value={`$${log.estimated_cost_usd.toFixed(4)}`} />}
              </>
            )}
            {children && (
              <span style={blockStyles.toggle}>{open ? "▲" : "▼"}</span>
            )}
          </div>
        </div>
        {open && children && (
          <div style={blockStyles.body}>{children}</div>
        )}
        {log?.error_message && (
          <p style={{ margin: "0.3rem 0 0", fontSize: "0.8rem", color: C.red }}>{log.error_message}</p>
        )}
      </div>
    </div>
  );
}

function Score({ label, value }: { label: string; value: number }) {
  const color = value >= 8 ? C.green : value >= 6 ? C.amber : C.red;
  return (
    <span style={{ fontSize: "0.72rem", color, fontWeight: 600, marginRight: "0.5rem" }}>
      {label}: {value}/10
    </span>
  );
}

function Chip({ label, mono }: { label: string; mono?: boolean }) {
  return (
    <span style={{
      fontSize: "0.72rem",
      background: C.bgMuted,
      color: C.textSec,
      padding: "0.1rem 0.4rem",
      borderRadius: 4,
      fontFamily: mono ? F.mono : F.sans,
    }}>
      {label}
    </span>
  );
}

function Meta({ value }: { value: string }) {
  return (
    <span style={{ fontSize: "0.72rem", color: C.textMuted, fontFamily: F.mono }}>{value}</span>
  );
}

function ObjectOrText({ value }: { value: any }) {
  if (value == null) return null;
  if (typeof value === "string") {
    return <div style={{ fontSize: "0.83rem", lineHeight: 1.6, color: C.textSec, maxHeight: 300, overflowY: "auto" as const, whiteSpace: "pre-wrap" as const }}>{value}</div>;
  }
  // Object/array — render as structured key-value list
  const entries = Object.entries(value);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
      {entries.map(([k, v]) => (
        <div key={k}>
          <p style={{ margin: "0 0 0.2rem", fontSize: "0.7rem", fontWeight: 700, color: C.textMuted, textTransform: "uppercase" as const, letterSpacing: "0.05em" }}>
            {k.replace(/_/g, " ")}
          </p>
          {Array.isArray(v) ? (
            <ul style={{ margin: 0, paddingLeft: "1.1rem" }}>
              {(v as any[]).map((item, i) => (
                <li key={i} style={{ fontSize: "0.82rem", color: C.textSec, lineHeight: 1.5 }}>
                  {typeof item === "string" ? item : JSON.stringify(item)}
                </li>
              ))}
            </ul>
          ) : (
            <p style={{ margin: 0, fontSize: "0.82rem", color: C.textSec, lineHeight: 1.5, whiteSpace: "pre-wrap" as const }}>
              {typeof v === "string" ? v : JSON.stringify(v, null, 2)}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}

function EvalOutput({ evaluation, evalScore, evalFlags }: { evaluation: any; evalScore?: number; evalFlags?: string[] }) {
  const dim = evaluation?.dimension_scores ?? {};
  const flags = evalFlags ?? evaluation?.flags ?? [];
  return (
    <div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginBottom: "0.5rem" }}>
        {Object.entries(dim).map(([k, v]) => (
          <div key={k} style={{ background: C.bgSubtle, border: `1px solid ${C.border}`, borderRadius: 6, padding: "0.4rem 0.6rem", minWidth: 90 }}>
            <p style={{ margin: "0 0 0.15rem", fontSize: "0.7rem", color: C.textMuted, textTransform: "capitalize" as const }}>{k.replace(/_/g, " ")}</p>
            <p style={{ margin: 0, fontWeight: 700, color: (v as number) >= 8 ? C.green : (v as number) >= 6 ? C.amber : C.red }}>
              {v as number}/10
            </p>
          </div>
        ))}
      </div>
      {flags.length > 0 && (
        <div>
          {flags.map((f: string, i: number) => (
            <p key={i} style={{ margin: "0.15rem 0", fontSize: "0.8rem", color: C.amber }}>⚠ {f}</p>
          ))}
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  timeline: { display: "flex", flexDirection: "column" },
  empty: { padding: "2rem", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, textAlign: "center" },
  topicGrid: { display: "flex", flexDirection: "column", gap: "0.4rem" },
  topicCard: { border: `1px solid ${C.border}`, borderRadius: 6, padding: "0.65rem 0.75rem", background: C.bgSubtle },
  topicCardSelected: { border: `1px solid ${C.blue}`, background: C.blueLight },
  aiSelectedTag: { fontSize: "0.68rem", background: C.blue, color: "#fff", padding: "0.1rem 0.35rem", borderRadius: 3, fontWeight: 700, marginBottom: "0.3rem", display: "inline-block" },
  topicCardTitle: { margin: "0.2rem 0 0.2rem", fontWeight: 600, fontSize: "0.85rem", color: C.text },
  topicCardSummary: { margin: "0 0 0.3rem", fontSize: "0.78rem", color: C.textSec, lineHeight: 1.4 },
  scoreRow: { display: "flex", flexWrap: "wrap" },
  selectedTopicBox: { background: C.blueLight, border: `1px solid ${C.blue}22`, borderRadius: 6, padding: "0.75rem" },
  selectedTopicTitle: { margin: "0 0 0.3rem", fontWeight: 700, fontSize: "0.95rem" },
  selectedTopicReason: { margin: "0 0 0.4rem", fontSize: "0.83rem", color: C.textSec, lineHeight: 1.5 },
  chipRow: { display: "flex", gap: "0.35rem", flexWrap: "wrap", marginBottom: "0.3rem" },
  pocExpected: { margin: 0, fontSize: "0.82rem", color: C.textSec },
  textOutput: { fontSize: "0.83rem", lineHeight: 1.6, color: C.textSec, maxHeight: 300, overflowY: "auto" as const, background: C.bgSubtle, padding: "0.75rem", borderRadius: 4 },
  pocPlanBox: { background: C.bgSubtle, borderRadius: 6, padding: "0.75rem" },
  pocGoal: { margin: "0 0 0.4rem", fontSize: "0.85rem", color: C.text },
  depsRow: { display: "flex", gap: "0.35rem", flexWrap: "wrap" },
  fileListLabel: { margin: "0 0 0.3rem", fontSize: "0.72rem", color: C.textMuted, fontWeight: 600, textTransform: "uppercase" as const },
  fileRow: { display: "flex", gap: "0.5rem", alignItems: "baseline", marginBottom: "0.15rem" },
  filePath: { fontFamily: F.mono, fontSize: "0.78rem", color: C.blue },
  filePurpose: { fontSize: "0.75rem", color: C.textMuted },
  reviewBox: { border: "1px solid", borderRadius: 6, padding: "0.65rem 0.75rem" },
  rawJson: { margin: 0, fontSize: "0.75rem", background: "#0D1117", color: "#E6EDF3", padding: "0.75rem", borderRadius: 4, overflow: "auto", maxHeight: 300, fontFamily: F.mono },
};

const blockStyles: Record<string, React.CSSProperties> = {
  wrapper: { display: "flex", gap: "0.75rem", marginBottom: "0.1rem" },
  track: { display: "flex", flexDirection: "column", alignItems: "center", flexShrink: 0, width: 16 },
  dot: { width: 10, height: 10, borderRadius: "50%", flexShrink: 0, marginTop: 12 },
  line: { width: 1, flex: 1, background: C.border, minHeight: 12, marginTop: 2 },
  content: { flex: 1, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, marginBottom: "0.4rem", overflow: "hidden" },
  header: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.55rem 0.75rem", cursor: "pointer", gap: "0.5rem", flexWrap: "wrap" },
  headerLeft: { display: "flex", alignItems: "center", gap: "0.4rem", flex: 1, minWidth: 0 },
  agentName: { fontWeight: 600, fontSize: "0.82rem", color: C.text, whiteSpace: "nowrap" as const },
  statusDot: { fontSize: "0.75rem", fontWeight: 700, flexShrink: 0 },
  summary: { fontSize: "0.8rem", color: C.textSec, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" as const },
  headerRight: { display: "flex", alignItems: "center", gap: "0.5rem", flexShrink: 0 },
  toggle: { fontSize: "0.65rem", color: C.textMuted, cursor: "pointer" },
  body: { borderTop: `1px solid ${C.border}`, padding: "0.75rem" },
};
