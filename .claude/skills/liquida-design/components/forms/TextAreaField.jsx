import React from "react";

/**
 * Labeled multi-line input, same skin as Field.
 */
export function TextAreaField({ label, rows = 3, onChange, className = "", ...props }) {
  return (
    <label className={className} style={{ display: "block" }}>
      {label && <span className="r-label">{label}</span>}
      <textarea
        className="r-input"
        rows={rows}
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
        {...props}
      ></textarea>
    </label>
  );
}
