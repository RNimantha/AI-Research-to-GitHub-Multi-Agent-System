"use client";
import { C, F } from "../lib/design";

const PIPELINE: { key: string; label: string; hitl?: boolean }[] = [
  { key: "discovering", label: "Discover Topics" },
  { key: "awaiting_topic_approval", label: "Topic Approval", hitl: true },
  { key: "researching", label: "Research" },
  { key: "verifying_sources", label: "Verify Sources" },
  { key: "analyzing", label: "Technical Analysis" },
  { key: "writing_report", label: "Write Report" },
  { key: "awaiting_report_approval", label: "Report Approval", hitl: true },
  { key: "planning_poc", label: "Plan POC" },
  { key: "generating_code", label: "Generate Code" },
  { key: "reviewing_code", label: "Review Code" },
  { key: "evaluating", label: "Evaluate" },
  { key: "awaiting_improvement_approval", label: "Improvement Review", hitl: true },
  { key: "improving", label: "Apply Improvements" },
  { key: "awaiting_github_approval", label: "GitHub Approval", hitl: true },
  { key: "publishing", label: "Publish" },
  { key: "complete", label: "Complete" },
];

interface Props {
  status: string;
}

export default function StatusTimeline({ status }: Props) {
  const isFailed = status === "failed";
  const currentIdx = PIPELINE.findIndex((s) => s.key === status);

  return (
    <div style={styles.container}>
      {PIPELINE.map((step, i) => {
        const isDone = !isFailed && i < currentIdx;
        const isCurrent = !isFailed && i === currentIdx;
        const isHitl = !!step.hitl;

        let dotColor: string = C.border;
        let labelColor: string = C.textMuted;
        let labelWeight: React.CSSProperties["fontWeight"] = 400;

        if (isDone) { dotColor = C.green; labelColor = C.textSec; }
        if (isCurrent && !isHitl) { dotColor = C.blue; labelColor = C.text; labelWeight = 600; }
        if (isCurrent && isHitl) { dotColor = C.amber; labelColor = C.amber; labelWeight = 700; }
        if (isFailed) { dotColor = C.border; labelColor = C.textMuted; }

        return (
          <div key={step.key} style={styles.row}>
            <div style={styles.track}>
              <div style={{ ...styles.dot, background: dotColor, ...(isCurrent && !isHitl ? styles.dotActive : {}) }} />
              {i < PIPELINE.length - 1 && (
                <div style={{ ...styles.connector, background: isDone ? C.green : C.border }} />
              )}
            </div>
            <span style={{ ...styles.label, color: labelColor, fontWeight: labelWeight }}>
              {step.label}
              {isHitl && !isDone && (
                <span style={{ ...styles.hitlTag, opacity: isCurrent ? 1 : 0.4 }}>HITL</span>
              )}
              {isCurrent && !isFailed && (
                <span style={{ ...styles.nowTag, background: isHitl ? C.amberLight : C.blueLight, color: isHitl ? C.amber : C.blue }}>
                  now
                </span>
              )}
            </span>
          </div>
        );
      })}

      {isFailed && (
        <div style={styles.row}>
          <div style={styles.track}>
            <div style={{ ...styles.dot, background: C.red }} />
          </div>
          <span style={{ ...styles.label, color: C.red, fontWeight: 700 }}>Failed</span>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: { display: "flex", flexDirection: "column" },
  row: { display: "flex", gap: "0.5rem", alignItems: "flex-start", minHeight: 24 },
  track: { display: "flex", flexDirection: "column", alignItems: "center", flexShrink: 0, width: 14, paddingTop: 2 },
  dot: { width: 8, height: 8, borderRadius: "50%", flexShrink: 0 },
  dotActive: { boxShadow: `0 0 0 3px ${C.blue}33` },
  connector: { width: 1, flex: 1, minHeight: 10, marginTop: 1 },
  label: { fontSize: "0.78rem", lineHeight: 1.4, paddingBottom: 4, display: "flex", alignItems: "center", gap: "0.3rem", flexWrap: "wrap" as const },
  hitlTag: { fontSize: "0.62rem", background: C.amberLight, color: C.amber, padding: "0 0.3rem", borderRadius: 3, fontWeight: 700, fontFamily: F.mono },
  nowTag: { fontSize: "0.62rem", padding: "0 0.3rem", borderRadius: 3, fontWeight: 700 },
};
