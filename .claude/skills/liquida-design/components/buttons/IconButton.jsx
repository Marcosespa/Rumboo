import React from "react";
import { Icon } from "../icons/Icon.jsx";

/**
 * 44px square bordered icon button (header refresh / logout actions).
 */
export function IconButton({ icon, label, size = 16, className = "", ...props }) {
  return (
    <button
      type="button"
      className={`r-iconbtn ${className}`.trim()}
      aria-label={label}
      title={label}
      {...props}
    >
      <Icon name={icon} size={size} />
    </button>
  );
}
