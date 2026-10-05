import React from "react";

/**
 * Rumbo button. Mirrors fleteControl's Button.jsx variants plus an
 * `accent` (ámbar señal) variant reserved for the main camera CTA.
 */
export function Button({
  variant = "primary",
  size,
  block = false,
  loading = false,
  as = "button",
  className = "",
  children,
  ...props
}) {
  const variantClass = variant === "lightGhost" ? "light-ghost" : variant;
  const cls = [
    "r-btn",
    `r-btn--${variantClass}`,
    size === "lg" ? "r-btn--lg" : "",
    block ? "r-btn--block" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");
  const Comp = as;
  return (
    <Comp className={cls} disabled={loading || props.disabled} {...props}>
      {loading ? (
        <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
          <span className="r-spinner"></span>
          <span>Espera...</span>
        </span>
      ) : (
        children
      )}
    </Comp>
  );
}
