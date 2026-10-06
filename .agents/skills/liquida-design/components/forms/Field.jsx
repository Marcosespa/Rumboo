import React from "react";

/**
 * Labeled text input. cloudSoft fill, line border; focus turns the
 * field paper-white with a primary border + soft ring.
 * Note: onChange receives the VALUE, not the event (matches product code).
 */
export function Field({ label, hint, className = "", onChange, ...props }) {
  return (
    <label className={className} style={{ display: "block" }}>
      {label && <span className="r-label">{label}</span>}
      <input
        className="r-input"
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
        {...props}
      />
      {hint && (
        <span
          style={{
            display: "block",
            marginTop: 6,
            fontSize: "var(--text-sm)",
            color: "var(--color-mist)",
          }}
        >
          {hint}
        </span>
      )}
    </label>
  );
}
