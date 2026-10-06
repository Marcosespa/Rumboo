import React from "react";

/**
 * Movement list row: title + meta on the left, signed amount on the right.
 * Amount color: expense = error (with minus), income/receivable = primary.
 */
export function ListRow({ title, meta, amount, tone = "neutral", className = "" }) {
  const color =
    tone === "expense"
      ? "var(--color-error)"
      : tone === "income"
        ? "var(--color-primary)"
        : "var(--color-ink)";
  return (
    <div className={`r-listrow ${className}`.trim()}>
      <div style={{ minWidth: 0 }}>
        <p style={{ margin: 0, fontSize: "var(--text-base)", fontWeight: 600, color: "var(--color-ink)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {title}
        </p>
        {meta && (
          <p style={{ margin: "4px 0 0", fontSize: "var(--text-base)", color: "var(--color-mist)" }}>
            {meta}
          </p>
        )}
      </div>
      <span style={{ flex: "none", fontSize: "var(--text-base)", fontWeight: 600, color }}>
        {tone === "expense" ? "-" : ""}
        {amount}
      </span>
    </div>
  );
}
