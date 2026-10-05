import React from "react";

/**
 * Segmented control — cloudSoft track, active segment goes ink/paper.
 * Used for login/register toggle and document-type pickers.
 */
export function SegmentedControl({ options = [], value, onChange, block = false, className = "" }) {
  return (
    <div className={`r-seg ${block ? "r-seg--block" : ""} ${className}`.trim()} role="tablist">
      {options.map((opt) => {
        const o = typeof opt === "string" ? { value: opt, label: opt } : opt;
        const active = value === o.value;
        return (
          <button
            key={o.value}
            type="button"
            role="tab"
            aria-selected={active}
            className={`r-seg__btn ${active ? "is-active" : ""}`.trim()}
            onClick={onChange ? () => onChange(o.value) : undefined}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
