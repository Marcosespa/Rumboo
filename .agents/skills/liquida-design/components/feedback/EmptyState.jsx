import React from "react";
import { Icon } from "../icons/Icon.jsx";

/**
 * Dashed empty state with icon box and friendly guidance copy.
 */
export function EmptyState({ icon = "Camera", text, className = "" }) {
  return (
    <div className={`r-subcard r-subcard--dashed ${className}`.trim()}>
      <div className="r-empty__icon">
        <Icon name={icon} size={16} />
      </div>
      <p
        style={{
          margin: "12px 0 0",
          fontSize: "var(--text-base)",
          lineHeight: "var(--leading-relaxed)",
          color: "var(--color-mist)",
        }}
      >
        {text}
      </p>
    </div>
  );
}
