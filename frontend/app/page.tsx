// app/page.tsx
// The main Authlytixs dashboard — shows all live sessions and alerts
"use client";

import { useEffect, useState } from "react";

const API = "http://localhost:8000";

// ── Types ────────────────────────────────────────────────────────────────────
type Session = {
  session_id: string;
  user_email: string;
  trust_score: number;
  is_flagged: boolean;
  ip_address: string;
  created_at: string;
};

type Alert = {
  id: string;
  user_email: string;
  trust_score: number;
  reason: string;
  severity: string;
  is_acknowledged: boolean;
  created_at: string;
};

// ── Helpers ──────────────────────────────────────────────────────────────────
function scoreColor(score: number) {
  if (score >= 70) return "#22c55e";   // green
  if (score >= 45) return "#f59e0b";   // amber
  return "#ef4444";                     // red
}

function scoreLabel(score: number) {
  if (score >= 70) return "Safe";
  if (score >= 45) return "Warning";
  return "Critical";
}

// ── Main Dashboard ────────────────────────────────────────────────────────────
export default function Dashboard() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [alerts, setAlerts]     = useState<Alert[]>([]);
  const [lastUpdated, setLastUpdated] = useState("");

  // Fetch sessions and alerts every 3 seconds
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sRes, aRes] = await Promise.all([
          fetch(`${API}/sessions/`),
          fetch(`${API}/alerts/`),
        ]);
        const sData = await sRes.json();
        const aData = await aRes.json();
        setSessions(sData.sessions || []);
        setAlerts(aData.alerts || []);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch {
        console.error("API not reachable");
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const avgScore = sessions.length
    ? Math.round(sessions.reduce((s, x) => s + x.trust_score, 0) / sessions.length)
    : 100;

  const flagged   = sessions.filter(s => s.is_flagged).length;
  const unackAlerts = alerts.filter(a => !a.is_acknowledged).length;

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0f172a",
      color: "#f1f5f9",
      fontFamily: "system-ui, sans-serif",
      padding: "24px",
    }}>

      {/* ── Header ── */}
      <div style={{ display: "flex", justifyContent: "space-between",
                    alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "24px", fontWeight: 700,
                       color: "#38bdf8", letterSpacing: "-0.5px" }}>
            Authlytixs
          </h1>
          <p style={{ margin: "2px 0 0", fontSize: "13px", color: "#64748b" }}>
            Continuous Identity Integrity Platform
          </p>
        </div>
        <div style={{ fontSize: "12px", color: "#475569" }}>
          <span style={{ display: "inline-block", width: 8, height: 8,
                         borderRadius: "50%", background: "#22c55e",
                         marginRight: 6, animation: "pulse 2s infinite" }}/>
          Live · updated {lastUpdated}
        </div>
      </div>

      {/* ── Metric Cards ── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)",
                    gap: "12px", marginBottom: "24px" }}>
        {[
          { label: "Active Sessions", value: sessions.length, color: "#38bdf8" },
          { label: "Avg Trust Score",  value: avgScore,        color: scoreColor(avgScore) },
          { label: "Flagged Sessions", value: flagged,         color: flagged ? "#ef4444" : "#22c55e" },
          { label: "Open Alerts",      value: unackAlerts,     color: unackAlerts ? "#f59e0b" : "#22c55e" },
        ].map(card => (
          <div key={card.label} style={{
            background: "#1e293b", borderRadius: "12px",
            padding: "16px", border: "1px solid #334155",
          }}>
            <div style={{ fontSize: "12px", color: "#64748b", marginBottom: "6px" }}>
              {card.label}
            </div>
            <div style={{ fontSize: "28px", fontWeight: 700, color: card.color }}>
              {card.value}
            </div>
          </div>
        ))}
      </div>

      {/* ── Sessions Table ── */}
      <div style={{ background: "#1e293b", borderRadius: "12px",
                    border: "1px solid #334155", marginBottom: "20px" }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid #334155",
                      display: "flex", justifyContent: "space-between" }}>
          <span style={{ fontWeight: 600 }}>Live Sessions</span>
          <span style={{ fontSize: "13px", color: "#475569" }}>
            {sessions.length} active
          </span>
        </div>

        {sessions.length === 0 ? (
          <div style={{ padding: "32px", textAlign: "center", color: "#475569" }}>
            No active sessions yet.{" "}
            <a href={`${API}/docs`} target="_blank"
               style={{ color: "#38bdf8" }}>
              Create one in the API docs ↗
            </a>
          </div>
        ) : (
          sessions.map(s => (
            <div key={s.session_id} style={{
              display: "flex", alignItems: "center", gap: "16px",
              padding: "14px 20px", borderBottom: "1px solid #1e293b",
            }}>
              {/* Status dot */}
              <div style={{
                width: 10, height: 10, borderRadius: "50%", flexShrink: 0,
                background: scoreColor(s.trust_score),
              }}/>

              {/* Email */}
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "14px", fontWeight: 500 }}>
                  {s.user_email}
                </div>
                <div style={{ fontSize: "12px", color: "#475569" }}>
                  {s.ip_address} · {s.session_id.slice(0, 8)}...
                </div>
              </div>

              {/* Trust score bar */}
              <div style={{ width: "140px" }}>
                <div style={{ height: 6, background: "#0f172a",
                              borderRadius: 3, overflow: "hidden" }}>
                  <div style={{
                    height: "100%", borderRadius: 3,
                    width: `${s.trust_score}%`,
                    background: scoreColor(s.trust_score),
                    transition: "width 0.5s ease",
                  }}/>
                </div>
              </div>

              {/* Score number */}
              <div style={{ fontSize: "18px", fontWeight: 700, minWidth: "36px",
                            color: scoreColor(s.trust_score), textAlign: "right" }}>
                {Math.round(s.trust_score)}
              </div>

              {/* Badge */}
              <div style={{
                fontSize: "11px", fontWeight: 600, padding: "3px 10px",
                borderRadius: "999px", minWidth: "60px", textAlign: "center",
                background: s.is_flagged ? "#450a0a" : "#052e16",
                color: s.is_flagged ? "#ef4444" : "#22c55e",
                border: `1px solid ${s.is_flagged ? "#ef4444" : "#22c55e"}33`,
              }}>
                {s.is_flagged ? "FLAGGED" : scoreLabel(s.trust_score)}
              </div>
            </div>
          ))
        )}
      </div>

      {/* ── Alerts Panel ── */}
      <div style={{ background: "#1e293b", borderRadius: "12px",
                    border: "1px solid #334155" }}>
        <div style={{ padding: "16px 20px", borderBottom: "1px solid #334155",
                      display: "flex", justifyContent: "space-between" }}>
          <span style={{ fontWeight: 600 }}>Recent Alerts</span>
          <span style={{ fontSize: "13px", color: "#475569" }}>
            {unackAlerts} unacknowledged
          </span>
        </div>

        {alerts.length === 0 ? (
          <div style={{ padding: "32px", textAlign: "center", color: "#475569" }}>
            No alerts yet — system is healthy ✅
          </div>
        ) : (
          alerts.slice(0, 5).map(a => (
            <div key={a.id} style={{
              display: "flex", gap: "12px", alignItems: "flex-start",
              padding: "14px 20px", borderBottom: "1px solid #0f172a",
            }}>
              <div style={{
                width: 8, height: 8, borderRadius: "50%", marginTop: 5,
                flexShrink: 0,
                background: a.severity === "critical" ? "#ef4444" : "#f59e0b",
              }}/>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "13px", fontWeight: 500,
                              marginBottom: "2px" }}>
                  {a.user_email}
                </div>
                <div style={{ fontSize: "12px", color: "#64748b" }}>
                  {a.reason}
                </div>
              </div>
              <div style={{ fontSize: "11px", color: "#475569",
                            whiteSpace: "nowrap" }}>
                Score: {Math.round(a.trust_score)}
              </div>
              <div style={{
                fontSize: "11px", padding: "2px 8px", borderRadius: "999px",
                background: a.severity === "critical" ? "#450a0a" : "#431407",
                color: a.severity === "critical" ? "#ef4444" : "#f59e0b",
              }}>
                {a.severity}
              </div>
            </div>
          ))
        )}
      </div>

    </div>
  );
}