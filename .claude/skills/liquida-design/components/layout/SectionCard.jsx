import React from "react";

/**
 * Section card — 28px radius paper panel with title/subtitle header
 * and optional right-aligned action. Direct port of SectionCard.jsx.
 */
export function SectionCard({ title, subtitle, action, children, className = "" }) {
  return (
    <section className={`r-card ${className}`.trim()}>
      {(title || subtitle || action) && (
        <div style={{ marginBottom: 16, display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
          <div style={{ minWidth: 0 }}>
            {title && (
              <h2 style={{ margin: 0, fontSize: "var(--text-body)", fontWeight: 600, letterSpacing: "var(--tracking-tight)", color: "var(--color-ink)" }}>
                {title}
              </h2>
            )}
            {subtitle && (
              <p style={{ margin: "4px 0 0", fontSize: "var(--text-base)", lineHeight: "var(--leading-relaxed)", color: "var(--color-mist)" }}>
                {subtitle}
              </p>
            )}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
