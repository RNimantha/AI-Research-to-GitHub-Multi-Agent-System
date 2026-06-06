"use client";
import { useEffect, useState } from "react";
import { api } from "../../../lib/api";
import Link from "next/link";
import MarkdownViewer from "../../../components/MarkdownViewer";
import CodeViewer from "../../../components/CodeViewer";
import SourceList from "../../../components/SourceList";
import ReportView from "../../../components/ReportView";

interface ReportDetailProps {
  params: { topic_slug: string };
}

export default function ReportDetail({ params }: ReportDetailProps) {
  const { topic_slug } = params;
  const [report, setReport] = useState<any>(null);
  const [markdown, setMarkdown] = useState<string>("");
  const [activeTab, setActiveTab] = useState<"report" | "code" | "sources" | "eval">("report");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getReport(topic_slug),
      api.getReportMarkdown(topic_slug).catch(() => null),
    ])
      .then(([data, md]: any) => {
        setReport(data.report ?? data);
        if (md?.markdown) setMarkdown(md.markdown);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [topic_slug]);

  if (loading) return <p style={{ fontFamily: "monospace", padding: "2rem" }}>Loading…</p>;
  if (error) return <p style={{ fontFamily: "monospace", padding: "2rem", color: "red" }}>{error}</p>;
  if (!report) return null;

  const rj = report.report_json ?? report;
  const poc = rj.poc ?? report.poc ?? {};
  const files = poc.files ?? [];
  const sources = rj.sources ?? report.sources ?? [];

  return (
    <div style={{ fontFamily: "monospace", maxWidth: 1000, margin: "0 auto", padding: "2rem" }}>
      <div style={styles.breadcrumb}>
        <Link href="/reports" style={{ color: "#0969da" }}>Reports</Link>
        <span style={{ margin: "0 0.5rem", color: "#656d76" }}>/</span>
        <span>{topic_slug}</span>
      </div>

      <h1 style={styles.title}>{report.topic_name}</h1>
      {report.one_liner && <p style={styles.oneLiner}>{report.one_liner}</p>}

      <div style={styles.metaRow}>
        {report.eval_score != null && (
          <span style={{
            ...styles.scoreBadge,
            color: report.eval_score >= 8 ? "#2da44e" : report.eval_score >= 7 ? "#fb8f44" : "#da3633",
            background: report.eval_score >= 8 ? "#2da44e11" : report.eval_score >= 7 ? "#fb8f4411" : "#da363311",
          }}>
            Score: {report.eval_score.toFixed(1)}/10
          </span>
        )}
        {(report.tags ?? []).map((t: string) => (
          <span key={t} style={styles.tag}>{t}</span>
        ))}
        {report.github_url && (
          <a href={report.github_url} target="_blank" rel="noreferrer" style={styles.ghLink}>
            View on GitHub →
          </a>
        )}
      </div>

      <div style={styles.tabBar}>
        {(["report", "code", "sources", "eval"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{ ...styles.tab, ...(activeTab === tab ? styles.activeTab : {}) }}
          >
            {tab === "report" ? "Report" : tab === "code" ? `Code (${files.length})` : tab === "sources" ? `Sources (${sources.length})` : "Evaluation"}
          </button>
        ))}
      </div>

      {activeTab === "report" && (
        <div style={styles.tabContent}>
          {report.report_json ? (
            <ReportView report={report.report_json} />
          ) : markdown ? (
            <MarkdownViewer content={markdown} />
          ) : (
            <pre style={styles.rawJson}>{JSON.stringify(report, null, 2)}</pre>
          )}
        </div>
      )}

      {activeTab === "code" && (
        <div style={styles.tabContent}>
          {poc.project_name && (
            <div style={styles.pocMeta}>
              <strong>{poc.project_name}</strong>
              {poc.goal && <p style={{ margin: "0.25rem 0 0", color: "#444" }}>{poc.goal}</p>}
              {poc.run_instructions && (
                <pre style={styles.runInstructions}>{poc.run_instructions}</pre>
              )}
              {(poc.dependencies ?? []).length > 0 && (
                <p style={{ margin: "0.5rem 0 0", fontSize: "0.85rem" }}>
                  Dependencies: {poc.dependencies.join(", ")}
                </p>
              )}
            </div>
          )}
          <CodeViewer files={files} />
        </div>
      )}

      {activeTab === "sources" && (
        <div style={styles.tabContent}>
          <SourceList sources={sources} />
        </div>
      )}

      {activeTab === "eval" && (
        <div style={styles.tabContent}>
          <EvalDisplay report={report.report_json ?? report} evalScore={report.eval_score} evalFlags={report.eval_flags} />
        </div>
      )}
    </div>
  );
}

function ReportSections({ report }: { report: any }) {
  const sections = [
    ["Executive Summary", report.executive_summary],
    ["What It Is", report.what_it_is],
    ["Why It Matters Now", report.why_it_matters_now],
    ["Problem It Solves", report.problem_it_solves],
    ["How It Works (Simple)", report.how_it_works_simple],
    ["How It Works (Technical)", report.how_it_works_technical],
    ["Architecture", report.architecture],
    ["Ecosystem Placement", report.ecosystem_placement],
    ["Real-World Implementations", report.real_world_implementations],
    ["Limitations", report.limitations],
    ["Future Outlook", report.future_outlook],
  ].filter(([, v]) => v);

  return (
    <div>
      {sections.map(([label, content]) => (
        <div key={label as string} style={{ marginBottom: "1.5rem" }}>
          <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem", fontWeight: 700 }}>{label as string}</h3>
          <p style={{ margin: 0, lineHeight: 1.7, color: "#1f2328" }}>{content as string}</p>
        </div>
      ))}
      {(report.use_cases ?? []).length > 0 && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem", fontWeight: 700 }}>Use Cases</h3>
          <ul>{report.use_cases.map((u: string, i: number) => <li key={i}>{u}</li>)}</ul>
        </div>
      )}
      {(report.alternatives ?? []).length > 0 && (
        <div>
          <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem", fontWeight: 700 }}>Alternatives</h3>
          <ul>{report.alternatives.map((a: string, i: number) => <li key={i}>{a}</li>)}</ul>
        </div>
      )}
    </div>
  );
}

function EvalDisplay({ report, evalScore, evalFlags }: { report: any; evalScore?: number; evalFlags?: string[] }) {
  const scores = report.evaluation?.dimension_scores ?? {};
  const flags = evalFlags ?? report.eval_flags ?? report.evaluation?.flags ?? [];
  const improvements = report.evaluation?.improvements ?? [];

  return (
    <div>
      <div style={styles.evalGrid}>
        {Object.entries(scores).map(([dim, score]) => (
          <div key={dim} style={styles.evalCard}>
            <div style={styles.evalDim}>{dim.replace(/_/g, " ")}</div>
            <div style={{ ...styles.evalScore, color: (score as number) >= 8 ? "#2da44e" : (score as number) >= 6 ? "#fb8f44" : "#da3633" }}>
              {score as number}/10
            </div>
          </div>
        ))}
      </div>
      {flags.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <h4 style={{ margin: "0 0 0.5rem" }}>Flags</h4>
          <ul>{flags.map((f: string, i: number) => <li key={i} style={{ color: "#da3633" }}>{f}</li>)}</ul>
        </div>
      )}
      {improvements.length > 0 && (
        <div style={{ marginTop: "1rem" }}>
          <h4 style={{ margin: "0 0 0.5rem" }}>Suggested Improvements</h4>
          <ul>{improvements.map((imp: string, i: number) => <li key={i}>{imp}</li>)}</ul>
        </div>
      )}
      {flags.length === 0 && improvements.length === 0 && Object.keys(scores).length === 0 && (
        <pre style={styles.rawJson}>{JSON.stringify(report.evaluation, null, 2)}</pre>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  breadcrumb: { fontSize: "0.85rem", marginBottom: "0.75rem", color: "#656d76" },
  title: { margin: "0 0 0.5rem", fontSize: "1.75rem" },
  oneLiner: { margin: "0 0 0.75rem", color: "#444", fontSize: "1rem", fontStyle: "italic" },
  metaRow: { display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center", marginBottom: "1.25rem" },
  scoreBadge: { fontWeight: 700, fontSize: "0.9rem", padding: "0.2rem 0.6rem", borderRadius: 4 },
  tag: { fontSize: "0.75rem", background: "#e1e4e8", borderRadius: 4, padding: "0.15rem 0.4rem" },
  ghLink: { color: "#2da44e", fontWeight: 600, fontSize: "0.85rem", textDecoration: "none" },
  tabBar: { display: "flex", borderBottom: "1px solid #d0d7de", marginBottom: "1.25rem", gap: 0 },
  tab: { padding: "0.5rem 1rem", border: "none", background: "transparent", cursor: "pointer", fontFamily: "monospace", fontSize: "0.85rem", color: "#656d76", borderBottom: "2px solid transparent" },
  activeTab: { color: "#1f2328", fontWeight: 700, borderBottom: "2px solid #0969da" },
  tabContent: { minHeight: "200px" },
  pocMeta: { border: "1px solid #d0d7de", borderRadius: 6, padding: "0.75rem", background: "#f6f8fa", marginBottom: "0.75rem" },
  runInstructions: { background: "#0d1117", color: "#e6edf3", padding: "0.75rem", borderRadius: 4, fontSize: "0.82rem", margin: "0.5rem 0 0", overflowX: "auto" },
  evalGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "0.5rem" },
  evalCard: { border: "1px solid #d0d7de", borderRadius: 6, padding: "0.6rem 0.75rem", background: "#f6f8fa" },
  evalDim: { fontSize: "0.75rem", color: "#656d76", textTransform: "capitalize", marginBottom: "0.25rem" },
  evalScore: { fontSize: "1.2rem", fontWeight: 700 },
  rawJson: { background: "#f6f8fa", padding: "1rem", overflow: "auto", fontSize: "0.8rem", borderRadius: 6 },
};
