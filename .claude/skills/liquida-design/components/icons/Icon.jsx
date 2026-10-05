import React from "react";

/**
 * Lucide icon adapter. Rumbo uses the Lucide icon set (the product code
 * imports lucide-react). Load the Lucide UMD bundle once per page:
 *   <script src="https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js"></script>
 * then <Icon name="Camera" /> renders the real Lucide path data.
 */
export function Icon({ name, size = 16, strokeWidth = 2, color = "currentColor", style = {}, ...props }) {
  const registry =
    typeof window !== "undefined" && window.lucide && window.lucide.icons
      ? window.lucide.icons
      : null;
  const node = registry ? registry[name] : null;

  if (!node) {
    return (
      <span
        aria-hidden="true"
        style={{ display: "inline-block", width: size, height: size, flex: "none", ...style }}
      ></span>
    );
  }

  let kids = node;
  if (typeof node[0] === "string") kids = node[2] || [];

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      style={{ flex: "none", ...style }}
      {...props}
    >
      {kids.map((child, i) => {
        const tag = child[0];
        const attrs = child[1] || {};
        return React.createElement(tag, { ...attrs, key: i });
      })}
    </svg>
  );
}
