import React from "react";
import { StatusPill } from "./StatusPill.jsx";

/**
 * Alert/receivable card: cloudSoft surface (error-tinted when critical),
 * title + detail + meta line, status pill, optional action row.
 */
export function AlertCard({
  severity = "attention",
  title,
  detail,
  meta,
  pill = true,
  actions,
  className = "",
}) {
  const critical = severity === "critical";
  return (
    <div className={`r-subcard ${critical ? "r-subcard--error" : ""} ${className}`.trim()}>
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
        <div style={{ minWidth: 0 }}>
          <p style={{ margin: 0, fontSize: "var(--text-base)", fontWeight: 600, color: "var(--color-ink)" }}>
            {title}
          </p>
          {detail && (
            <p style={{ margin: "4px 0 0", fontSize: "var(--text-base)", lineHeight: "var(--leading-relaxed)", color: "var(--color-mist)" }}>
              {detail}
            </p>
          )}
          {meta && (
            <p style={{ margin: "8px 0 0", fontSize: "var(--text-xs)", textTransform: "uppercase", letterSpacing: "0.16em", color: "var(--color-mist)" }}>
              {meta}
            </p>
          )}
        </div>
        {pill && (
          <StatusPill status={critical ? "critical" : "attention"} solid={critical}>
            {critical ? "Urgente" : "Atención"}
          </StatusPill>
        )}
      </div>
      {actions && (
        <div style={{ marginTop: 16, display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))" }}>
          {actions}
        </div>
      )}
    </div>
  );
}
