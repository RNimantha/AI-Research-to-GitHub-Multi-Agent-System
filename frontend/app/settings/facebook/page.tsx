"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../../lib/api";
import { C, F } from "../../../lib/design";

interface FBSettings {
  facebook_page_access_token_set: boolean;
  facebook_page_access_token_preview: string;
  facebook_page_id: string;
  facebook_auto_post: boolean;
}

export default function FacebookSettingsPage() {
  const [saved, setSaved] = useState<FBSettings | null>(null);
  const [token, setToken] = useState("");
  const [pageId, setPageId] = useState("");
  const [autoPost, setAutoPost] = useState(false);
  const [showToken, setShowToken] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [testError, setTestError] = useState("");

  useEffect(() => {
    api.getFacebookSettings().then((d: any) => {
      setSaved(d);
      setPageId(d.facebook_page_id || "");
      setAutoPost(d.facebook_auto_post ?? false);
    }).catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaveMsg("");
    try {
      const payload: any = { facebook_page_id: pageId, facebook_auto_post: autoPost };
      if (token) payload.facebook_page_access_token = token;
      await api.saveFacebookSettings(payload);
      const fresh: any = await api.getFacebookSettings();
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
      const r = await api.testFacebookConnection();
      setTestResult(r);
    } catch (e: any) {
      setTestError(e.message);
    } finally {
      setTesting(false);
    }
  };

  const connected = saved?.facebook_page_access_token_set && saved?.facebook_page_id;

  return (
    <div style={styles.page}>
      <div style={styles.breadcrumb}>
        <Link href="/dashboard" style={styles.breadLink}>Dashboard</Link>
        <span style={styles.sep}>/</span>
        <span style={styles.breadCur}>Facebook Settings</span>
      </div>

      <h1 style={styles.heading}>Facebook Integration</h1>
      <p style={styles.sub}>Automatically post published research reports to your Facebook Page.</p>

      {/* Status */}
      <div style={{ ...styles.statusCard, borderColor: connected ? C.green : C.amber, background: connected ? C.greenLight : C.amberLight }}>
        <span style={{ ...styles.statusDot, background: connected ? C.green : C.amber }} />
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: connected ? C.green : C.amber }}>
          {connected
            ? `Connected — token: ${saved?.facebook_page_access_token_preview}`
            : "Not connected — token or Page ID missing"}
        </span>
        {connected && saved?.facebook_page_id && (
          <span style={styles.chip}>Page {saved.facebook_page_id}</span>
        )}
      </div>

      {/* Credentials form */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Credentials</p>

        <Field label="Page Access Token" hint={saved?.facebook_page_access_token_set ? "Token saved. Paste new value to replace." : "Generate from Facebook Graph API Explorer."}>
          <div style={styles.tokenRow}>
            <input
              type={showToken ? "text" : "password"}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder={saved?.facebook_page_access_token_set ? "••••••••••••  (leave blank to keep)" : "EAAxxxxxxxx..."}
              style={styles.input}
              autoComplete="off"
            />
            <button onClick={() => setShowToken(!showToken)} style={styles.eyeBtn}>
              {showToken ? "hide" : "show"}
            </button>
          </div>
        </Field>

        <Field label="Page ID" hint="The numeric ID of your Facebook Page (e.g. 123456789012345).">
          <input
            type="text"
            value={pageId}
            onChange={(e) => setPageId(e.target.value)}
            placeholder="123456789012345"
            style={{ ...styles.input, maxWidth: 240 }}
          />
        </Field>

        <Field label="Auto-post after GitHub publish">
          <label style={styles.toggle}>
            <input
              type="checkbox"
              checked={autoPost}
              onChange={(e) => setAutoPost(e.target.checked)}
              style={{ marginRight: "0.5rem" }}
            />
            <span style={{ fontSize: "0.85rem", color: C.textSec }}>
              Automatically post to Facebook when a report is approved and pushed to GitHub
            </span>
          </label>
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

      {/* Test */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Test connection</p>
        <p style={styles.hint}>Verifies the Page Access Token and returns Page details.</p>
        <button onClick={handleTest} disabled={testing || !connected} style={styles.testBtn}>
          {testing ? "Testing…" : "Test connection"}
        </button>
        {testError && (
          <div style={styles.errBox}>
            <strong>Error:</strong> {testError}
          </div>
        )}
        {testResult && (
          <div style={testResult.connected ? styles.successBox : styles.errBox}>
            {testResult.connected ? (
              <>
                <p style={{ margin: "0 0 0.4rem", fontWeight: 700, color: C.green }}>
                  Connected — {testResult.page_name}
                </p>
                <pre style={styles.pre}>{JSON.stringify(testResult, null, 2)}</pre>
              </>
            ) : (
              <p style={{ margin: 0, color: C.red }}>{testResult.error}</p>
            )}
          </div>
        )}
      </div>

      {/* How to get a token */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>How to get a Page Access Token</p>
        <ol style={styles.ol}>
          <li>Go to <strong>Facebook Developers</strong> → your App → <strong>Graph API Explorer</strong></li>
          <li>Select your App in the top-right dropdown</li>
          <li>Click <strong>Generate Access Token</strong> and grant <code>pages_manage_posts</code> and <code>pages_read_engagement</code></li>
          <li>In the left panel, run: <code>GET /me/accounts</code> — copy the <code>access_token</code> for your Page</li>
          <li>To get a long-lived token (60 days), exchange via:<br />
            <code>GET /oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN</code>
          </li>
          <li>Paste the Page Access Token and Page ID above</li>
        </ol>

        <div style={{ marginTop: "1rem", padding: "0.75rem", background: C.amberLight, border: `1px solid ${C.amber}44`, borderRadius: 6 }}>
          <p style={{ margin: 0, fontSize: "0.8rem", color: C.amber, fontWeight: 600 }}>
            Note: Page Access Tokens expire after 60 days unless you generate a non-expiring one via the App Dashboard.
            For production, use a System User with permanent tokens.
          </p>
        </div>
      </div>

      {/* What gets posted */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>What gets posted</p>
        <p style={styles.hint}>When a report is published to GitHub, this connector posts:</p>
        <pre style={{ ...styles.pre, background: C.bgMuted, padding: "0.75rem", borderRadius: 5, marginTop: "0.25rem" }}>
{`New Research Report: [Topic Name]

[One-liner summary]

Eval Score: 8.4/10
Tags: #LLM #AgenticAI #RAG

Read the full report and runnable POC: https://github.com/...`}
        </pre>
        <p style={{ ...styles.hint, marginTop: "0.75rem" }}>
          You can also manually trigger a post from any completed run detail page.
        </p>
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
  chip: { fontFamily: F.mono, fontSize: "0.75rem", background: C.bgMuted, color: C.textSec, padding: "0.1rem 0.45rem", borderRadius: 4, marginLeft: "auto" },
  card: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "1.1rem 1.25rem", marginBottom: "1rem" },
  cardTitle: { margin: "0 0 0.9rem", fontSize: "0.82rem", fontWeight: 700, color: C.text, textTransform: "uppercase" as const, letterSpacing: "0.05em" },
  hint: { margin: "0 0 0.75rem", fontSize: "0.82rem", color: C.textMuted },
  tokenRow: { display: "flex", gap: "0.4rem" },
  input: { flex: 1, padding: "0.45rem 0.65rem", border: `1px solid ${C.border}`, borderRadius: 5, fontSize: "0.85rem", fontFamily: F.mono, color: C.text, background: C.bgSubtle, outline: "none" },
  eyeBtn: { padding: "0.4rem 0.65rem", border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", background: C.bgMuted, fontSize: "0.75rem", color: C.textSec, fontFamily: F.sans, flexShrink: 0 },
  toggle: { display: "flex", alignItems: "center", cursor: "pointer" },
  actions: { display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem" },
  saveBtn: { padding: "0.5rem 1.1rem", background: C.blue, color: "#fff", border: "none", borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  testBtn: { padding: "0.45rem 1rem", background: C.bgMuted, color: C.text, border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  errBox: { marginTop: "0.75rem", background: C.redLight, border: `1px solid ${C.red}44`, borderRadius: 5, padding: "0.6rem 0.75rem", fontSize: "0.83rem", color: C.red },
  successBox: { marginTop: "0.75rem", background: C.greenLight, border: `1px solid ${C.green}44`, borderRadius: 5, padding: "0.6rem 0.75rem" },
  pre: { margin: 0, fontSize: "0.75rem", fontFamily: F.mono, color: C.textSec, overflowX: "auto" },
  ol: { margin: 0, paddingLeft: "1.25rem", display: "flex", flexDirection: "column" as const, gap: "0.5rem", fontSize: "0.83rem", color: C.textSec, lineHeight: 1.6 },
};

const fieldStyles: Record<string, React.CSSProperties> = {
  wrapper: { marginBottom: "1rem" },
  label: { display: "block", fontSize: "0.78rem", fontWeight: 700, color: C.text, marginBottom: "0.3rem" },
  hint: { margin: "0.25rem 0 0", fontSize: "0.75rem", color: C.textMuted },
};
