"use client";
import { useState } from "react";
import { C, F } from "../lib/design";

interface ReportJson {
  topic_name?: string;
  topic_slug?: string;
  one_liner?: string;
  tags?: string[];
  created_at?: string;
  executive_summary?: string;
  what_it_is?: string;
  why_it_matters_now?: string;
  problem_it_solves?: string;
  how_it_works_simple?: string;
  how_it_works_technical?: string;
  architecture?: string;
  ecosystem_placement?: string;
  real_world_implementations?: string;
  use_cases?: string[];
  limitations?: string;
  alternatives?: string[];
  future_outlook?: string;
  eval_score?: number;
  eval_flags?: string[];
  poc?: {
    project_name?: string;
    goal?: string;
    run_instructions?: string;
    dependencies?: string[];
    limitations?: string[];
  };
  sources?: Array<{
    title: string;
    url: string;
    source_type?: string;
    credibility_score?: number;
  }>;
}

interface Props {
  report: ReportJson;
}

// Inline span: handles **bold** and [link](url) within a single string
function InlineSpan({ text }: { text: string }): React.ReactElement {
  const TOKEN_RE = /(\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?:\/\/[^)]+)\))/g;
  const nodes: React.ReactNode[] = [];
  let last = 0;
  let m: RegExpExecArray | null;
  while ((m = TOKEN_RE.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    if (m[0].startsWith("**")) {
      nodes.push(<strong key={m.index}>{m[2]}</strong>);
    } else {
      nodes.push(
        <a key={m.index} href={m[4]} target="_blank" rel="noreferrer"
          style={{ color: "#0969da", textDecoration: "underline" }}>
          {m[3]}
        </a>
      );
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return <>{nodes}</>;
}

// RichText: detects structure and renders appropriately
function RichText({ text }: { text: string }) {
  if (!text) return null;

  // Pattern: inline numbered items  (1) foo (2) bar (3) baz
  const INLINE_NUM_RE = /^\s*\(1\)\s+/;
  if (INLINE_NUM_RE.test(text)) {
    const parts = text.split(/\s*\(\d+\)\s+/).filter(Boolean);
    if (parts.length > 1) {
      return (
        <ol style={richStyles.ol}>
          {parts.map((item, i) => (
            <li key={i} style={richStyles.li}><InlineSpan text={item.trim()} /></li>
          ))}
        </ol>
      );
    }
  }

  // Pattern: line-based list — lines starting with "- ", "• ", "* ", or "N. "
  const lines = text.split("\n");
  const BULLET_RE = /^[-•*]\s+(.+)/;
  const NUM_LINE_RE = /^\d+[.)]\s+(.+)/;
  const isBulletList = lines.length > 1 && lines.filter(l => BULLET_RE.test(l.trim())).length >= lines.filter(l => l.trim()).length * 0.6;
  const isNumList = lines.length > 1 && lines.filter(l => NUM_LINE_RE.test(l.trim())).length >= lines.filter(l => l.trim()).length * 0.6;

  if (isBulletList) {
    return (
      <ul style={richStyles.ul}>
        {lines.filter(l => l.trim()).map((line, i) => {
          const m = line.trim().match(BULLET_RE);
          return <li key={i} style={richStyles.li}><InlineSpan text={m ? m[1] : line.trim()} /></li>;
        })}
      </ul>
    );
  }

  if (isNumList) {
    return (
      <ol style={richStyles.ol}>
        {lines.filter(l => l.trim()).map((line, i) => {
          const m = line.trim().match(NUM_LINE_RE);
          return <li key={i} style={richStyles.li}><InlineSpan text={m ? m[1] : line.trim()} /></li>;
        })}
      </ol>
    );
  }

  // Pattern: multiple paragraphs separated by blank lines
  if (text.includes("\n\n")) {
    const paragraphs = text.split(/\n\n+/).filter(p => p.trim());
    if (paragraphs.length > 1) {
      return (
        <>
          {paragraphs.map((p, i) => (
            <p key={i} style={{ margin: "0 0 0.75rem", lineHeight: 1.75 }}>
              <InlineSpan text={p.trim()} />
            </p>
          ))}
        </>
      );
    }
  }

  // Default: single paragraph with inline formatting
  return <InlineSpan text={text} />;
}

const richStyles: Record<string, React.CSSProperties> = {
  ul: { margin: "0.25rem 0 0.5rem", paddingLeft: "1.4rem", lineHeight: 1.75 },
  ol: { margin: "0.25rem 0 0.5rem", paddingLeft: "1.4rem", lineHeight: 1.75 },
  li: { marginBottom: "0.35rem" },
};

export default function ReportView({ report }: Props) {
  const [activeSection, setActiveSection] = useState<string | null>(null);

  const sections = [
    { id: "summary", label: "Summary", icon: "◈" },
    { id: "what", label: "What It Is", icon: "○" },
    { id: "why", label: "Why It Matters", icon: "▲" },
    { id: "how", label: "How It Works", icon: "⬡" },
    { id: "architecture", label: "Architecture", icon: "⊞" },
    { id: "usecases", label: "Use Cases", icon: "✦" },
    { id: "poc", label: "POC", icon: "⌥" },
    { id: "limitations", label: "Limitations", icon: "⚑" },
    { id: "sources", label: "Sources", icon: "⊕" },
  ].filter((s) => hasSectionData(s.id, report));

  return (
    <div style={styles.wrapper}>
      {/* Report header */}
      <div style={styles.reportHeader}>
        <div style={styles.reportMeta}>
          {report.topic_slug && (
            <span style={styles.slug}>{report.topic_slug}</span>
          )}
          {report.created_at && (
            <span style={styles.date}>{new Date(report.created_at).toLocaleDateString()}</span>
          )}
        </div>
        <h1 style={styles.reportTitle}>{report.topic_name}</h1>
        {report.one_liner && <p style={styles.oneLiner}>{report.one_liner}</p>}
        <div style={styles.tagRow}>
          {(report.tags ?? []).map((t) => <Tag key={t} label={t} />)}
          {report.eval_score != null && (
            <span style={{
              ...styles.scoreTag,
              color: report.eval_score >= 8 ? C.green : report.eval_score >= 7 ? C.amber : C.red,
              background: report.eval_score >= 8 ? C.greenLight : report.eval_score >= 7 ? C.amberLight : C.redLight,
            }}>
              Score: {report.eval_score.toFixed(1)}/10
            </span>
          )}
        </div>
        {(report.eval_flags ?? []).length > 0 && (
          <div style={styles.flagsRow}>
            {report.eval_flags!.map((f, i) => (
              <span key={i} style={styles.flag}>⚑ {f}</span>
            ))}
          </div>
        )}
      </div>

      {/* Section nav */}
      <div style={styles.sectionNav}>
        {sections.map((s) => (
          <a
            key={s.id}
            href={`#report-${s.id}`}
            style={styles.sectionNavLink}
          >
            <span style={styles.sectionNavIcon}>{s.icon}</span>
            {s.label}
          </a>
        ))}
      </div>

      {/* Sections */}
      <div style={styles.sections}>

        {report.executive_summary && (
          <Section id="summary" title="Executive Summary" icon="◈" accent={C.blue}>
            <p style={styles.summaryText}><RichText text={report.executive_summary} /></p>
          </Section>
        )}

        {(report.what_it_is || report.problem_it_solves) && (
          <Section id="what" title="What It Is" icon="○">
            {report.what_it_is && <p style={styles.bodyText}><RichText text={report.what_it_is} /></p>}
            {report.problem_it_solves && (
              <Callout title="Problem it solves" color={C.blue}>
                {report.problem_it_solves}
              </Callout>
            )}
          </Section>
        )}

        {report.why_it_matters_now && (
          <Section id="why" title="Why It Matters Now" icon="▲" accent={C.amber}>
            <p style={styles.bodyText}><RichText text={report.why_it_matters_now} /></p>
          </Section>
        )}

        {(report.how_it_works_simple || report.how_it_works_technical) && (
          <Section id="how" title="How It Works" icon="⬡">
            {report.how_it_works_simple && (
              <div style={styles.howBlock}>
                <p style={styles.howLabel}>Simple view</p>
                <p style={styles.bodyText}><RichText text={report.how_it_works_simple} /></p>
              </div>
            )}
            {report.how_it_works_technical && (
              <div style={styles.howBlock}>
                <p style={{ ...styles.howLabel, color: C.purple }}>Technical view</p>
                <p style={styles.bodyText}><RichText text={report.how_it_works_technical} /></p>
              </div>
            )}
          </Section>
        )}

        {(report.architecture || report.ecosystem_placement) && (
          <Section id="architecture" title="Architecture & Ecosystem" icon="⊞">
            {report.architecture && (
              <div style={styles.howBlock}>
                <p style={styles.howLabel}>Architecture</p>
                <p style={styles.bodyText}><RichText text={report.architecture} /></p>
              </div>
            )}
            {report.ecosystem_placement && (
              <div style={styles.howBlock}>
                <p style={styles.howLabel}>Ecosystem placement</p>
                <p style={styles.bodyText}><RichText text={report.ecosystem_placement} /></p>
              </div>
            )}
            {report.real_world_implementations && (
              <div style={styles.howBlock}>
                <p style={styles.howLabel}>Real-world implementations</p>
                <p style={styles.bodyText}><RichText text={report.real_world_implementations} /></p>
              </div>
            )}
          </Section>
        )}

        {((report.use_cases ?? []).length > 0 || (report.alternatives ?? []).length > 0) && (
          <Section id="usecases" title="Use Cases & Alternatives" icon="✦">
            {(report.use_cases ?? []).length > 0 && (
              <div style={{ marginBottom: "0.75rem" }}>
                <p style={styles.howLabel}>Use cases</p>
                <ul style={styles.list}>
                  {report.use_cases!.map((u, i) => (
                    <li key={i} style={styles.listItem}><RichText text={u} /></li>
                  ))}
                </ul>
              </div>
            )}
            {(report.alternatives ?? []).length > 0 && (
              <div>
                <p style={styles.howLabel}>Alternatives</p>
                <div style={styles.altRow}>
                  {report.alternatives!.map((a, i) => (
                    <span key={i} style={styles.altChip}>{a}</span>
                  ))}
                </div>
              </div>
            )}
          </Section>
        )}

        {report.poc && (
          <Section id="poc" title="Proof of Concept" icon="⌥" accent={C.green}>
            <div style={styles.pocBox}>
              {report.poc.project_name && (
                <p style={styles.pocName}>{report.poc.project_name}</p>
              )}
              {report.poc.goal && (
                <p style={styles.pocGoal}>{report.poc.goal}</p>
              )}
              {(report.poc.dependencies ?? []).length > 0 && (
                <div style={styles.depsSection}>
                  <p style={styles.howLabel}>Dependencies</p>
                  <div style={styles.depsRow}>
                    {report.poc.dependencies!.map((d) => (
                      <code key={d} style={styles.depChip}>{d}</code>
                    ))}
                  </div>
                </div>
              )}
              {report.poc.run_instructions && (
                <div style={styles.depsSection}>
                  <p style={styles.howLabel}>Run instructions</p>
                  <pre style={styles.runInstructions}>{report.poc.run_instructions}</pre>
                </div>
              )}
              {(report.poc.limitations ?? []).length > 0 && (
                <div style={styles.depsSection}>
                  <p style={styles.howLabel}>POC limitations</p>
                  <ul style={styles.list}>
                    {report.poc.limitations!.map((l, i) => (
                      <li key={i} style={styles.listItem}>{l}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Section>
        )}

        {(report.limitations || report.future_outlook) && (
          <Section id="limitations" title="Limitations & Future Outlook" icon="⚑" accent={C.amber}>
            {report.limitations && (
              <Callout title="Limitations" color={C.amber}>
                {report.limitations}
              </Callout>
            )}
            {report.future_outlook && (
              <div style={{ marginTop: "0.75rem" }}>
                <p style={styles.howLabel}>Future outlook</p>
                <p style={styles.bodyText}><RichText text={report.future_outlook} /></p>
              </div>
            )}
          </Section>
        )}

        {(report.sources ?? []).length > 0 && (
          <Section id="sources" title={`Sources (${report.sources!.length})`} icon="⊕">
            <div style={styles.sourcesList}>
              {report.sources!.map((s, i) => (
                <div key={i} style={styles.sourceRow}>
                  <span style={styles.sourceNum}>{i + 1}</span>
                  <div style={styles.sourceBody}>
                    <a href={s.url} target="_blank" rel="noreferrer" style={styles.sourceTitle}>
                      {s.title}
                    </a>
                    <div style={styles.sourceMeta}>
                      {s.source_type && <span style={styles.sourceType}>{s.source_type}</span>}
                      {s.credibility_score != null && (
                        <span style={{
                          ...styles.credScore,
                          color: s.credibility_score >= 0.8 ? C.green : s.credibility_score >= 0.6 ? C.amber : C.red,
                        }}>
                          {(s.credibility_score * 10).toFixed(1)}/10
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}

      </div>
    </div>
  );
}

function Section({ id, title, icon, accent, children }: {
  id: string;
  title: string;
  icon: string;
  accent?: string;
  children: React.ReactNode;
}) {
  return (
    <div id={`report-${id}`} style={sectionStyles.wrapper}>
      <div style={sectionStyles.header}>
        <span style={{ ...sectionStyles.icon, color: accent ?? C.textMuted }}>{icon}</span>
        <h2 style={sectionStyles.title}>{title}</h2>
        {accent && <div style={{ ...sectionStyles.accent, background: accent }} />}
      </div>
      <div style={sectionStyles.body}>{children}</div>
    </div>
  );
}

function Callout({ title, color, children }: { title: string; color: string; children: string }) {
  return (
    <div style={{ ...calloutStyles.box, borderLeftColor: color, background: `${color}08` }}>
      <p style={{ ...calloutStyles.title, color }}>{title}</p>
      <p style={calloutStyles.text}><RichText text={children} /></p>
    </div>
  );
}

function Tag({ label }: { label: string }) {
  return (
    <span style={{ fontSize: "0.72rem", background: C.bgMuted, color: C.textSec, padding: "0.15rem 0.4rem", borderRadius: 4, fontWeight: 500 }}>
      {label}
    </span>
  );
}

function hasSectionData(id: string, r: ReportJson): boolean {
  switch (id) {
    case "summary": return !!r.executive_summary;
    case "what": return !!(r.what_it_is || r.problem_it_solves);
    case "why": return !!r.why_it_matters_now;
    case "how": return !!(r.how_it_works_simple || r.how_it_works_technical);
    case "architecture": return !!(r.architecture || r.ecosystem_placement || r.real_world_implementations);
    case "usecases": return (r.use_cases?.length ?? 0) > 0 || (r.alternatives?.length ?? 0) > 0;
    case "poc": return !!r.poc;
    case "limitations": return !!(r.limitations || r.future_outlook);
    case "sources": return (r.sources?.length ?? 0) > 0;
    default: return false;
  }
}

const styles: Record<string, React.CSSProperties> = {
  wrapper: { fontFamily: F.sans },
  reportHeader: { background: `linear-gradient(135deg, ${C.blueLight} 0%, ${C.bgSubtle} 100%)`, border: `1px solid ${C.border}`, borderRadius: 10, padding: "1.5rem 1.75rem", marginBottom: "1rem" },
  reportMeta: { display: "flex", gap: "0.75rem", alignItems: "center", marginBottom: "0.5rem" },
  slug: { fontFamily: F.mono, fontSize: "0.72rem", color: C.textMuted },
  date: { fontSize: "0.72rem", color: C.textMuted },
  reportTitle: { margin: "0 0 0.4rem", fontSize: "1.6rem", fontWeight: 800, color: C.text, lineHeight: 1.2 },
  oneLiner: { margin: "0 0 0.75rem", fontSize: "1rem", color: C.textSec, fontStyle: "italic", lineHeight: 1.5 },
  tagRow: { display: "flex", gap: "0.35rem", flexWrap: "wrap", alignItems: "center" },
  scoreTag: { fontSize: "0.78rem", fontWeight: 700, padding: "0.2rem 0.55rem", borderRadius: 5 },
  flagsRow: { display: "flex", gap: "0.35rem", flexWrap: "wrap", marginTop: "0.5rem" },
  flag: { fontSize: "0.72rem", background: C.amberLight, color: C.amber, padding: "0.15rem 0.45rem", borderRadius: 4, fontWeight: 600 },
  sectionNav: { display: "flex", gap: "0.25rem", flexWrap: "wrap", marginBottom: "1rem", padding: "0.6rem 0.75rem", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 7 },
  sectionNavLink: { display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.78rem", color: C.textSec, textDecoration: "none", padding: "0.25rem 0.5rem", borderRadius: 4 },
  sectionNavIcon: { fontSize: "0.7rem", color: C.textMuted },
  sections: { display: "flex", flexDirection: "column", gap: "0.75rem" },
  summaryText: { margin: 0, fontSize: "0.95rem", color: C.text, lineHeight: 1.7, fontStyle: "italic" },
  bodyText: { margin: 0, fontSize: "0.88rem", color: C.textSec, lineHeight: 1.7 },
  howBlock: { marginBottom: "0.75rem" },
  howLabel: { margin: "0 0 0.3rem", fontSize: "0.7rem", fontWeight: 700, color: C.textMuted, textTransform: "uppercase" as const, letterSpacing: "0.06em" },
  list: { margin: "0", paddingLeft: "1.25rem" },
  listItem: { fontSize: "0.87rem", color: C.textSec, lineHeight: 1.6, marginBottom: "0.2rem" },
  altRow: { display: "flex", gap: "0.35rem", flexWrap: "wrap" },
  altChip: { fontSize: "0.8rem", background: C.bgMuted, color: C.text, padding: "0.2rem 0.6rem", borderRadius: 5, fontWeight: 500 },
  pocBox: { background: C.greenLight, border: `1px solid ${C.green}33`, borderRadius: 7, padding: "0.85rem" },
  pocName: { margin: "0 0 0.2rem", fontFamily: F.mono, fontWeight: 700, fontSize: "0.95rem", color: C.text },
  pocGoal: { margin: "0 0 0.6rem", fontSize: "0.85rem", color: C.textSec, lineHeight: 1.5 },
  depsSection: { marginTop: "0.6rem" },
  depsRow: { display: "flex", gap: "0.35rem", flexWrap: "wrap" },
  depChip: { fontSize: "0.78rem", background: "#0D1117", color: "#E6EDF3", padding: "0.15rem 0.45rem", borderRadius: 4, fontFamily: F.mono },
  runInstructions: { margin: "0.3rem 0 0", background: "#0D1117", color: "#E6EDF3", padding: "0.75rem", borderRadius: 5, fontSize: "0.8rem", fontFamily: F.mono, overflowX: "auto", lineHeight: 1.5 },
  sourcesList: { display: "flex", flexDirection: "column", gap: "0.5rem" },
  sourceRow: { display: "flex", gap: "0.6rem", alignItems: "flex-start" },
  sourceNum: { width: 20, height: 20, borderRadius: "50%", background: C.bgMuted, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.65rem", fontWeight: 700, color: C.textMuted, flexShrink: 0, marginTop: 2 },
  sourceBody: { flex: 1 },
  sourceTitle: { fontSize: "0.85rem", color: C.blue, textDecoration: "none", fontWeight: 500, lineHeight: 1.4 },
  sourceMeta: { display: "flex", gap: "0.4rem", marginTop: "0.2rem" },
  sourceType: { fontSize: "0.68rem", background: C.bgMuted, color: C.textSec, padding: "0.05rem 0.3rem", borderRadius: 3 },
  credScore: { fontSize: "0.68rem", fontWeight: 700 },
};

const sectionStyles: Record<string, React.CSSProperties> = {
  wrapper: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" },
  header: { display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.7rem 1rem", borderBottom: `1px solid ${C.border}`, background: C.bgSubtle },
  icon: { fontSize: "0.9rem", flexShrink: 0 },
  title: { margin: 0, fontSize: "0.9rem", fontWeight: 700, color: C.text, flex: 1 },
  accent: { width: 3, height: 16, borderRadius: 2, flexShrink: 0 },
  body: { padding: "0.9rem 1rem" },
};

const calloutStyles: Record<string, React.CSSProperties> = {
  box: { borderLeft: "3px solid", borderRadius: "0 6px 6px 0", padding: "0.6rem 0.85rem", marginBottom: "0.5rem" },
  title: { margin: "0 0 0.25rem", fontSize: "0.72rem", fontWeight: 700, textTransform: "uppercase" as const, letterSpacing: "0.05em" },
  text: { margin: 0, fontSize: "0.87rem", color: C.textSec, lineHeight: 1.6 },
};
