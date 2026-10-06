import React from "react";

/**
 * Labeled select, same skin as Field. Options accept strings or
 * { value, label } objects.
 */
export function SelectField({ label, options = [], onChange, className = "", ...props }) {
  return (
    <label className={className} style={{ display: "block" }}>
      {label && <span className="r-label">{label}</span>}
      <select
        className="r-input"
        onChange={onChange ? (event) => onChange(event.target.value) : undefined}
        {...props}
      >
        {options.map((opt) => {
          const o = typeof opt === "string" ? { value: opt, label: opt } : opt;
          return (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          );
        })}
      </select>
    </label>
  );
}
