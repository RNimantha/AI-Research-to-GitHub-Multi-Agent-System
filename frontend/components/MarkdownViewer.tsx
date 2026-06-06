"use client";

interface Props {
  content: string;
}

export default function MarkdownViewer({ content }: Props) {
  const lines = content.split("\n");

  const renderLine = (line: string, i: number) => {
    if (/^######\s/.test(line)) return <h6 key={i} style={styles.h6}>{line.slice(7)}</h6>;
    if (/^#####\s/.test(line)) return <h5 key={i} style={styles.h5}>{line.slice(6)}</h5>;
    if (/^####\s/.test(line)) return <h4 key={i} style={styles.h4}>{line.slice(5)}</h4>;
    if (/^###\s/.test(line)) return <h3 key={i} style={styles.h3}>{line.slice(4)}</h3>;
    if (/^##\s/.test(line)) return <h2 key={i} style={styles.h2}>{line.slice(3)}</h2>;
    if (/^#\s/.test(line)) return <h1 key={i} style={styles.h1}>{line.slice(2)}</h1>;
    if (/^---+$/.test(line.trim())) return <hr key={i} style={styles.hr} />;
    if (line.trim() === "") return <div key={i} style={{ height: "0.75rem" }} />;
    if (/^[-*]\s/.test(line)) return <li key={i} style={styles.li}>{renderInline(line.slice(2))}</li>;
    if (/^\d+\.\s/.test(line)) return <li key={i} style={styles.li}>{renderInline(line.replace(/^\d+\.\s/, ""))}</li>;
    return <p key={i} style={styles.p}>{renderInline(line)}</p>;
  };

  const renderInline = (text: string): React.ReactNode => {
    const parts: React.ReactNode[] = [];
    let remaining = text;
    let idx = 0;

    while (remaining.length > 0) {
      const bold = remaining.match(/\*\*(.+?)\*\*/);
      const code = remaining.match(/`(.+?)`/);
      const link = remaining.match(/\[(.+?)\]\((https?:\/\/[^\s)]+)\)/);

      const candidates = [
        bold ? { type: "bold", index: bold.index!, match: bold } : null,
        code ? { type: "code", index: code.index!, match: code } : null,
        link ? { type: "link", index: link.index!, match: link } : null,
      ].filter(Boolean) as { type: string; index: number; match: RegExpMatchArray }[];

      if (candidates.length === 0) {
        parts.push(<span key={idx++}>{remaining}</span>);
        break;
      }

      candidates.sort((a, b) => a.index - b.index);
      const first = candidates[0];

      if (first.index > 0) {
        parts.push(<span key={idx++}>{remaining.slice(0, first.index)}</span>);
      }

      if (first.type === "bold") {
        parts.push(<strong key={idx++}>{first.match[1]}</strong>);
        remaining = remaining.slice(first.index + first.match[0].length);
      } else if (first.type === "code") {
        parts.push(<code key={idx++} style={styles.inlineCode}>{first.match[1]}</code>);
        remaining = remaining.slice(first.index + first.match[0].length);
      } else if (first.type === "link") {
        parts.push(
          <a key={idx++} href={first.match[2]} target="_blank" rel="noreferrer" style={styles.link}>
            {first.match[1]}
          </a>
        );
        remaining = remaining.slice(first.index + first.match[0].length);
      }
    }

    return <>{parts}</>;
  };

  // Group consecutive code fence blocks
  const rendered: React.ReactNode[] = [];
  let inCodeBlock = false;
  let codeLines: string[] = [];
  let codeLang = "";
  let lineIdx = 0;

  for (const line of lines) {
    if (!inCodeBlock && /^```/.test(line)) {
      inCodeBlock = true;
      codeLang = line.slice(3).trim();
      codeLines = [];
    } else if (inCodeBlock && /^```$/.test(line)) {
      inCodeBlock = false;
      rendered.push(
        <pre key={lineIdx++} style={styles.codeBlock}>
          <code>{codeLines.join("\n")}</code>
        </pre>
      );
    } else if (inCodeBlock) {
      codeLines.push(line);
    } else {
      rendered.push(renderLine(line, lineIdx++));
    }
  }

  if (inCodeBlock && codeLines.length > 0) {
    rendered.push(
      <pre key={lineIdx++} style={styles.codeBlock}>
        <code>{codeLines.join("\n")}</code>
      </pre>
    );
  }

  return <div style={styles.container}>{rendered}</div>;
}

const styles: Record<string, React.CSSProperties> = {
  container: { fontFamily: "Georgia, serif", lineHeight: 1.7, color: "#1f2328", maxWidth: "100%" },
  h1: { fontSize: "1.75rem", fontWeight: 700, marginBottom: "0.5rem", borderBottom: "1px solid #d0d7de", paddingBottom: "0.25rem" },
  h2: { fontSize: "1.4rem", fontWeight: 700, marginBottom: "0.4rem", marginTop: "1.5rem", borderBottom: "1px solid #d0d7de", paddingBottom: "0.2rem" },
  h3: { fontSize: "1.2rem", fontWeight: 700, marginTop: "1.2rem", marginBottom: "0.3rem" },
  h4: { fontSize: "1.05rem", fontWeight: 600, marginTop: "1rem", marginBottom: "0.3rem" },
  h5: { fontSize: "0.95rem", fontWeight: 600, marginTop: "0.8rem" },
  h6: { fontSize: "0.85rem", fontWeight: 600, color: "#656d76", marginTop: "0.8rem" },
  p: { margin: "0.3rem 0" },
  li: { marginLeft: "1.5rem", listStyle: "disc", marginBottom: "0.2rem" },
  hr: { border: "none", borderTop: "1px solid #d0d7de", margin: "1rem 0" },
  inlineCode: { background: "#f6f8fa", border: "1px solid #d0d7de", borderRadius: 3, padding: "0.1em 0.3em", fontFamily: "monospace", fontSize: "0.9em" },
  codeBlock: { background: "#0d1117", color: "#e6edf3", padding: "1rem", borderRadius: 6, overflowX: "auto", fontSize: "0.85rem", fontFamily: "monospace", margin: "0.75rem 0" },
  link: { color: "#0969da", textDecoration: "underline" },
};
