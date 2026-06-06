"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { C, F } from "../lib/design";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/runs", label: "Runs" },
  { href: "/reports", label: "Reports" },
];

export default function Nav() {
  const pathname = usePathname();

  return (
    <nav style={styles.nav}>
      <div style={styles.inner}>
        <Link href="/dashboard" style={styles.logo}>
          <span style={styles.logoMark}>▲</span>
          <span style={styles.logoText}>ARAS</span>
          <span style={styles.logoSub}>Research Ops</span>
        </Link>

        <div style={styles.links}>
          {links.map((l) => {
            const active = pathname === l.href || (l.href !== "/dashboard" && pathname.startsWith(l.href));
            return (
              <Link key={l.href} href={l.href} style={{ ...styles.link, ...(active ? styles.linkActive : {}) }}>
                {l.label}
              </Link>
            );
          })}
        </div>

        <div style={styles.right}>
          <Link
            href="/settings/github"
            style={{ ...styles.settingsLink, ...(pathname.startsWith("/settings/github") ? styles.settingsActive : {}) }}
          >
            GitHub
          </Link>
          <Link
            href="/settings/supabase"
            style={{ ...styles.settingsLink, ...(pathname.startsWith("/settings/supabase") ? styles.settingsActive : {}) }}
          >
            Supabase
          </Link>
        </div>
      </div>
    </nav>
  );
}

const styles: Record<string, React.CSSProperties> = {
  nav: {
    position: "sticky",
    top: 0,
    zIndex: 100,
    background: C.bg,
    borderBottom: `1px solid ${C.border}`,
    height: 56,
    display: "flex",
    alignItems: "center",
  },
  inner: {
    maxWidth: 1200,
    margin: "0 auto",
    padding: "0 1.5rem",
    width: "100%",
    display: "flex",
    alignItems: "center",
    gap: "2rem",
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: "0.5rem",
    textDecoration: "none",
    flexShrink: 0,
  },
  logoMark: {
    fontSize: "0.9rem",
    color: C.blue,
  },
  logoText: {
    fontFamily: F.mono,
    fontWeight: 700,
    fontSize: "0.95rem",
    color: C.text,
    letterSpacing: "-0.02em",
  },
  logoSub: {
    fontSize: "0.72rem",
    color: C.textMuted,
    fontFamily: F.sans,
    marginLeft: "0.1rem",
  },
  links: {
    display: "flex",
    gap: "0.25rem",
    flex: 1,
  },
  link: {
    padding: "0.35rem 0.65rem",
    borderRadius: 6,
    textDecoration: "none",
    fontSize: "0.85rem",
    color: C.textSec,
    fontFamily: F.sans,
    fontWeight: 500,
  },
  linkActive: {
    background: C.bgMuted,
    color: C.text,
  },
  right: {
    marginLeft: "auto",
    flexShrink: 0,
    display: "flex",
    gap: "0.4rem",
  },
  settingsLink: {
    fontSize: "0.78rem",
    color: C.textMuted,
    textDecoration: "none",
    fontFamily: F.sans,
    padding: "0.3rem 0.6rem",
    borderRadius: 4,
    border: `1px solid ${C.border}`,
  },
  settingsActive: {
    color: C.text,
    background: C.bgMuted,
    borderColor: C.borderStrong,
  },
};
