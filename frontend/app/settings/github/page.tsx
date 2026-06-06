"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../../lib/api";
import { C, F } from "../../../lib/design";

interface GHSettings {
  github_token_set: boolean;
  github_token_preview: string;
  github_repo_owner: string;
  github_repo_name: string;
  github_default_branch: string;
}

export default function GithubSettingsPage() {
  const [saved, setSaved] = useState<GHSettings | null>(null);
  const [token, setToken] = useState("");
  const [owner, setOwner] = useState("");
  const [repo, setRepo] = useState("");
  const [branch, setBranch] = useState("main");
  const [showToken, setShowToken] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testError, setTestError] = useState("");
  const [saveMsg, setSaveMsg] = useState("");

  useEffect(() => {
    api.getGithubSettings().then((d: any) => {
      setSaved(d);
      setOwner(d.github_repo_owner || "");
      setRepo(d.github_repo_name || "");
      setBranch(d.github_default_branch || "main");
    }).catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg("");
    try {
      const payload: any = { github_repo_owner: owner, github_repo_name: repo, github_default_branch: branch };
      if (token) payload.github_token = token;
      await api.saveGithubSettings(payload);
      const fresh: any = await api.getGithubSettings();
      setSaved(fresh);
      setToken("");
      setSaveMsg("Saved.");
      setTimeout(() => setSaveMsg(""), 3000);
    } catch (e: any) {
      setSaveMsg(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    setTestError("");
    try {
      const r = await api.testGithubConnection();
      setTestResult(r);
    } catch (e: any) {
      setTestError(e.message);
    } finally {
      setTesting(false);
    }
  };

  const tokenConnected = saved?.github_token_set;

  return (
    <div style={styles.page}>
      <div style={styles.breadcrumb}>
        <Link href="/dashboard" style={styles.breadLink}>Dashboard</Link>
        <span style={styles.sep}>/</span>
        <span style={styles.breadCur}>GitHub Settings</span>
      </div>

      <h1 style={styles.heading}>GitHub Integration</h1>
      <p style={styles.sub}>Connect your knowledge-base repository for publishing approved research artifacts.</p>

      {/* Status card */}
      <div style={{ ...styles.statusCard, borderColor: tokenConnected ? C.green : C.amber, background: tokenConnected ? C.greenLight : C.amberLight }}>
        <span style={{ ...styles.statusDot, background: tokenConnected ? C.green : C.amber }} />
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: tokenConnected ? C.green : C.amber }}>
          {tokenConnected ? `Connected — token: ${saved?.github_token_preview}` : "Not connected — token missing"}
        </span>
        {tokenConnected && saved?.github_repo_owner && (
          <span style={styles.repoChip}>
            {saved.github_repo_owner}/{saved.github_repo_name}
          </span>
        )}
      </div>

      {/* Form */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Credentials</p>

        <Field label="GitHub Personal Access Token" hint={saved?.github_token_set ? "Token saved. Paste new value to replace." : "Paste your fine-grained PAT."}>
          <div style={styles.tokenRow}>
            <input
              type={showToken ? "text" : "password"}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder={saved?.github_token_set ? "••••••••••••  (leave blank to keep)" : "github_pat_..."}
              style={styles.input}
              autoComplete="off"
            />
            <button onClick={() => setShowToken(!showToken)} style={styles.eyeBtn}>
              {showToken ? "hide" : "show"}
            </button>
          </div>
        </Field>

        <Field label="Repository owner" hint="Your GitHub username or org name.">
          <input
            type="text"
            value={owner}
            onChange={(e) => setOwner(e.target.value)}
            placeholder="your-github-username"
            style={styles.input}
          />
        </Field>

        <Field label="Repository name" hint="The knowledge-base repo (will be created if it doesn't exist).">
          <input
            type="text"
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            placeholder="trend2poc-knowledge-base"
            style={styles.input}
          />
        </Field>

        <Field label="Default branch">
          <input
            type="text"
            value={branch}
            onChange={(e) => setBranch(e.target.value)}
            placeholder="main"
            style={{ ...styles.input, maxWidth: 180 }}
          />
        </Field>

        <div style={styles.actions}>
          <button onClick={handleSave} disabled={saving} style={styles.saveBtn}>
            {saving ? "Saving…" : "Save settings"}
          </button>
          {saveMsg && (
            <span style={{ fontSize: "0.82rem", color: saveMsg.startsWith("Error") ? C.red : C.green, fontWeight: 600 }}>
              {saveMsg}
            </span>
          )}
        </div>
      </div>

      {/* Test connection */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Test connection</p>
        <p style={styles.hint}>Verifies token is valid and the repo is accessible.</p>
        <button onClick={handleTest} disabled={testing || !tokenConnected} style={styles.testBtn}>
          {testing ? "Testing…" : "Test connection"}
        </button>
        {testError && (
          <div style={styles.errBox}>
            <strong>Error:</strong> {testError}
          </div>
        )}
        {testResult && (
          <div style={styles.successBox}>
            <p style={{ margin: "0 0 0.4rem", fontWeight: 700, color: C.green }}>Connected</p>
            <pre style={styles.pre}>{JSON.stringify(testResult, null, 2)}</pre>
          </div>
        )}
      </div>

      {/* PAT instructions */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>How to create a fine-grained PAT</p>
        <ol style={styles.ol}>
          <li>GitHub → <strong>Settings</strong> → <strong>Developer settings</strong> → <strong>Personal access tokens</strong> → <strong>Fine-grained tokens</strong></li>
          <li>Click <strong>Generate new token</strong></li>
          <li>Set <strong>Repository access</strong> → Only selected → pick your knowledge-base repo</li>
          <li>Under <strong>Permissions → Repository permissions</strong>, set <strong>Contents</strong> to <em>Read and write</em> and <strong>Metadata</strong> to <em>Read-only</em></li>
          <li>Copy the token and paste it above</li>
        </ol>
      </div>
    </div>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div style={fieldStyles.wrapper}>
      <label style={fieldStyles.label}>{label}</label>
      {children}
      {hint && <p style={fieldStyles.hint}>{hint}</p>}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: { maxWidth: 680, margin: "0 auto", fontFamily: F.sans },
  breadcrumb: { display: "flex", alignItems: "center", gap: "0.35rem", marginBottom: "1.25rem" },
  breadLink: { fontSize: "0.82rem", color: C.blue, textDecoration: "none" },
  sep: { fontSize: "0.82rem", color: C.textMuted },
  breadCur: { fontSize: "0.82rem", color: C.textMuted },
  heading: { margin: "0 0 0.3rem", fontSize: "1.4rem", fontWeight: 800, color: C.text },
  sub: { margin: "0 0 1.25rem", fontSize: "0.9rem", color: C.textSec },
  statusCard: { display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap", border: "1px solid", borderRadius: 7, padding: "0.65rem 0.9rem", marginBottom: "1rem" },
  statusDot: { width: 8, height: 8, borderRadius: "50%", flexShrink: 0 },
  repoChip: { fontFamily: F.mono, fontSize: "0.75rem", background: C.bgMuted, color: C.textSec, padding: "0.1rem 0.45rem", borderRadius: 4, marginLeft: "auto" },
  card: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "1.1rem 1.25rem", marginBottom: "1rem" },
  cardTitle: { margin: "0 0 0.9rem", fontSize: "0.82rem", fontWeight: 700, color: C.text, textTransform: "uppercase" as const, letterSpacing: "0.05em" },
  hint: { margin: "0 0 0.75rem", fontSize: "0.82rem", color: C.textMuted },
  tokenRow: { display: "flex", gap: "0.4rem" },
  input: { flex: 1, padding: "0.45rem 0.65rem", border: `1px solid ${C.border}`, borderRadius: 5, fontSize: "0.85rem", fontFamily: F.mono, color: C.text, background: C.bgSubtle, outline: "none" },
  eyeBtn: { padding: "0.4rem 0.65rem", border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", background: C.bgMuted, fontSize: "0.75rem", color: C.textSec, fontFamily: F.sans, flexShrink: 0 },
  actions: { display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem" },
  saveBtn: { padding: "0.5rem 1.1rem", background: C.blue, color: "#fff", border: "none", borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  testBtn: { padding: "0.45rem 1rem", background: C.bgMuted, color: C.text, border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  errBox: { marginTop: "0.75rem", background: C.redLight, border: `1px solid ${C.red}44`, borderRadius: 5, padding: "0.6rem 0.75rem", fontSize: "0.83rem", color: C.red },
  successBox: { marginTop: "0.75rem", background: C.greenLight, border: `1px solid ${C.green}44`, borderRadius: 5, padding: "0.6rem 0.75rem" },
  pre: { margin: 0, fontSize: "0.75rem", fontFamily: F.mono, color: C.textSec, overflowX: "auto" },
  ol: { margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column" as const, gap: "0.4rem" },
};

const fieldStyles: Record<string, React.CSSProperties> = {
  wrapper: { marginBottom: "1rem" },
  label: { display: "block", fontSize: "0.78rem", fontWeight: 700, color: C.text, marginBottom: "0.3rem" },
  hint: { margin: "0.25rem 0 0", fontSize: "0.75rem", color: C.textMuted },
};
