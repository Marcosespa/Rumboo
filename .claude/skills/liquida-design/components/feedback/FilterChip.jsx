import React from "react";

/**
 * Round filter chip; active state is ink-filled.
 */
export function FilterChip({ active = false, onClick, children, className = "" }) {
  return (
    <button
      type="button"
      className={`r-chip ${active ? "is-active" : ""} ${className}`.trim()}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
