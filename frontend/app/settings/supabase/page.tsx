"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../../lib/api";
import { C, F } from "../../../lib/design";

export default function SupabaseSettingsPage() {
  const [url, setUrl] = useState("");
  const [anonKey, setAnonKey] = useState("");
  const [serviceKey, setServiceKey] = useState("");
  const [showAnon, setShowAnon] = useState(false);
  const [showService, setShowService] = useState(false);
  const [saved, setSaved] = useState<any>(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.getSupabaseSettings().then((d: any) => {
      setSaved(d);
      setUrl(d.supabase_url || "");
    }).catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMsg("");
    try {
      const payload: any = {};
      if (url) payload.supabase_url = url;
      if (anonKey) payload.supabase_anon_key = anonKey;
      if (serviceKey) payload.supabase_service_role_key = serviceKey;
      await api.saveSupabaseSettings(payload);
      const fresh: any = await api.getSupabaseSettings();
      setSaved(fresh);
      setAnonKey("");
      setServiceKey("");
      setMsg("Saved.");
      setTimeout(() => setMsg(""), 3000);
    } catch (e: any) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const r = await api.testSupabaseConnection();
      setTestResult(r);
    } catch (e: any) {
      setTestResult({ connected: false, error: e.message });
    } finally {
      setTesting(false);
    }
  };

  const isConnected = saved?.supabase_url_set && saved?.supabase_service_role_key_set;

  return (
    <div style={styles.page}>
      <div style={styles.breadcrumb}>
        <Link href="/dashboard" style={styles.breadLink}>Dashboard</Link>
        <span style={styles.sep}>/</span>
        <span style={styles.breadCur}>Supabase Settings</span>
      </div>

      <h1 style={styles.heading}>Supabase Integration</h1>
      <p style={styles.sub}>Connect your Supabase project to persist run history, reports, sources, and agent logs.</p>

      {/* Status */}
      <div style={{ ...styles.statusCard, borderColor: isConnected ? C.green : C.amber, background: isConnected ? C.greenLight : C.amberLight }}>
        <span style={{ ...styles.statusDot, background: isConnected ? C.green : C.amber }} />
        <span style={{ fontSize: "0.85rem", fontWeight: 600, color: isConnected ? C.green : C.amber }}>
          {isConnected ? `Connected — ${saved?.supabase_url}` : "Not configured"}
        </span>
        {saved?.supabase_service_role_key_set && (
          <span style={styles.chip}>service key: {saved.supabase_service_role_key_preview}</span>
        )}
      </div>

      {/* Form */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Project credentials</p>

        <Field label="Supabase URL">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://xxxx.supabase.co"
            style={styles.input}
          />
        </Field>

        <Field label="Anon / Public key" hint="Used by frontend clients (safe to expose).">
          <div style={styles.row}>
            <input
              type={showAnon ? "text" : "password"}
              value={anonKey}
              onChange={(e) => setAnonKey(e.target.value)}
              placeholder={saved?.supabase_anon_key_set ? `${saved.supabase_anon_key_preview}  (leave blank to keep)` : "eyJhbGciOi..."}
              style={styles.input}
              autoComplete="off"
            />
            <button onClick={() => setShowAnon(!showAnon)} style={styles.eyeBtn}>{showAnon ? "hide" : "show"}</button>
          </div>
        </Field>

        <Field label="Service role key" hint="Backend only — never expose to frontend or clients.">
          <div style={styles.row}>
            <input
              type={showService ? "text" : "password"}
              value={serviceKey}
              onChange={(e) => setServiceKey(e.target.value)}
              placeholder={saved?.supabase_service_role_key_set ? `${saved.supabase_service_role_key_preview}  (leave blank to keep)` : "eyJhbGciOi..."}
              style={styles.input}
              autoComplete="off"
            />
            <button onClick={() => setShowService(!showService)} style={styles.eyeBtn}>{showService ? "hide" : "show"}</button>
          </div>
        </Field>

        <div style={styles.actions}>
          <button onClick={handleSave} disabled={saving} style={styles.saveBtn}>
            {saving ? "Saving…" : "Save settings"}
          </button>
          {msg && (
            <span style={{ fontSize: "0.82rem", color: msg.startsWith("Error") ? C.red : C.green, fontWeight: 600 }}>
              {msg}
            </span>
          )}
        </div>
      </div>

      {/* Test */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Test connection</p>
        <p style={styles.hint}>Verifies credentials and checks that required tables exist.</p>
        <button onClick={handleTest} disabled={testing || !isConnected} style={styles.testBtn}>
          {testing ? "Testing…" : "Test connection"}
        </button>
        {testResult && (
          <div style={{
            ...styles.resultBox,
            background: testResult.connected ? C.greenLight : C.redLight,
            borderColor: testResult.connected ? `${C.green}44` : `${C.red}44`,
          }}>
            <p style={{ margin: "0 0 0.25rem", fontWeight: 700, color: testResult.connected ? C.green : C.red }}>
              {testResult.connected ? "Connected" : "Failed"}
            </p>
            {testResult.error && <p style={{ margin: 0, fontSize: "0.82rem", color: C.red }}>{testResult.error}</p>}
            {testResult.url && <p style={{ margin: 0, fontSize: "0.78rem", color: C.textMuted, fontFamily: F.mono }}>{testResult.url}</p>}
          </div>
        )}
      </div>

      {/* SQL setup card */}
      <div style={styles.card}>
        <p style={styles.cardTitle}>Database setup</p>
        <p style={styles.hint}>Run the SQL from <code>CLAUDE.md § 13</code> in your Supabase SQL editor to create all required tables and RLS policies.</p>
        <a
          href="https://supabase.com/dashboard"
          target="_blank"
          rel="noreferrer"
          style={styles.dbLink}
        >
          Open Supabase Dashboard →
        </a>
        <div style={styles.tableList}>
          {["research_runs","reports","sources","generated_files","approvals","agent_logs"].map((t) => (
            <span key={t} style={styles.tableChip}>{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: "1rem" }}>
      <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 700, color: C.text, marginBottom: "0.3rem" }}>{label}</label>
      {children}
      {hint && <p style={{ margin: "0.25rem 0 0", fontSize: "0.75rem", color: C.textMuted }}>{hint}</p>}
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
  chip: { fontFamily: F.mono, fontSize: "0.72rem", background: C.bgMuted, color: C.textSec, padding: "0.1rem 0.4rem", borderRadius: 4, marginLeft: "auto" },
  card: { background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "1.1rem 1.25rem", marginBottom: "1rem" },
  cardTitle: { margin: "0 0 0.9rem", fontSize: "0.82rem", fontWeight: 700, color: C.text, textTransform: "uppercase" as const, letterSpacing: "0.05em" },
  hint: { margin: "0 0 0.75rem", fontSize: "0.82rem", color: C.textMuted },
  row: { display: "flex", gap: "0.4rem" },
  input: { flex: 1, padding: "0.45rem 0.65rem", border: `1px solid ${C.border}`, borderRadius: 5, fontSize: "0.85rem", fontFamily: F.mono, color: C.text, background: C.bgSubtle, outline: "none" },
  eyeBtn: { padding: "0.4rem 0.65rem", border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", background: C.bgMuted, fontSize: "0.75rem", color: C.textSec, fontFamily: F.sans, flexShrink: 0 },
  actions: { display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem" },
  saveBtn: { padding: "0.5rem 1.1rem", background: C.blue, color: "#fff", border: "none", borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  testBtn: { padding: "0.45rem 1rem", background: C.bgMuted, color: C.text, border: `1px solid ${C.border}`, borderRadius: 5, cursor: "pointer", fontWeight: 600, fontSize: "0.85rem", fontFamily: F.sans },
  resultBox: { marginTop: "0.75rem", border: "1px solid", borderRadius: 5, padding: "0.6rem 0.75rem" },
  dbLink: { fontSize: "0.85rem", color: C.blue, fontWeight: 600 },
  tableList: { display: "flex", gap: "0.35rem", flexWrap: "wrap", marginTop: "0.75rem" },
  tableChip: { fontFamily: F.mono, fontSize: "0.75rem", background: C.bgMuted, color: C.textSec, padding: "0.15rem 0.45rem", borderRadius: 4 },
};
