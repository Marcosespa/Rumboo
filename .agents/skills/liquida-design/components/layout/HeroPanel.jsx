import React from "react";

export function Metric({ label, value }) {
  return (
    <div className="r-metric">
      <p className="r-metric__label">{label}</p>
      <p className="r-metric__value">{value}</p>
    </div>
  );
}

/**
 * Hero stat panel — the dark "answer" block at the top of each screen
 * (ink on Panel/Alertas, primary on Vehículos). Holds the protagonist
 * figure, a 3-up metric grid and light/lightGhost action buttons.
 */
export function HeroPanel({
  overline,
  figure,
  caption,
  tone = "ink",
  metrics = [],
  actions,
  children,
  className = "",
}) {
  return (
    <section className={`r-hero ${tone === "primary" ? "r-hero--primary" : ""} ${className}`.trim()}>
      {overline && <p className="r-overline">{overline}</p>}
      {figure && (
        <h2
          style={{
            margin: "12px 0 0",
            fontSize: "var(--text-figure)",
            fontWeight: 600,
            letterSpacing: "var(--tracking-tight)",
            fontFamily: "var(--font-display)",
          }}
        >
          {figure}
        </h2>
      )}
      {caption && (
        <p style={{ margin: "8px 0 0", maxWidth: "20rem", fontSize: "var(--text-base)", lineHeight: "var(--leading-relaxed)", opacity: 0.7 }}>
          {caption}
        </p>
      )}
      {metrics.length > 0 && (
        <div style={{ marginTop: 24, display: "grid", gridTemplateColumns: `repeat(${Math.min(metrics.length, 4)}, 1fr)`, gap: 12 }}>
          {metrics.map((m) => (
            <Metric key={m.label} label={m.label} value={m.value} />
          ))}
        </div>
      )}
      {actions && (
        <div style={{ marginTop: 24, display: "grid", gap: 12, gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))" }}>
          {actions}
        </div>
      )}
      {children}
    </section>
  );
}
