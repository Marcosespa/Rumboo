import React from "react";
import { Icon } from "../icons/Icon.jsx";

const DEFAULT_ITEMS = [
  { id: "dashboard", label: "Panel", icon: "ChartColumn" },
  { id: "vehicles", label: "Vehículos", icon: "CarFront" },
  { id: "alerts", label: "Alertas", icon: "Bell" },
  { id: "capture", label: "Foto", icon: "Camera" },
  { id: "verify", label: "Nuevo", icon: "PlusCircle" },
];

/**
 * Floating bottom navigation — pill bar with ink-filled active item and
 * an error badge on Alertas. Labels are always visible.
 */
export function BottomNav({
  items = DEFAULT_ITEMS,
  active,
  onSelect,
  badges = {},
  fixed = false,
  className = "",
}) {
  const bar = (
    <div className={`r-navbar ${className}`.trim()} style={{ width: "100%", maxWidth: "var(--content-max)" }}>
      {items.map((item) => {
        const badge = badges[item.id] || 0;
        return (
          <button
            key={item.id}
            type="button"
            className={`r-nav__item ${active === item.id ? "is-active" : ""}`.trim()}
            onClick={onSelect ? () => onSelect(item.id) : undefined}
          >
            <span style={{ position: "relative", display: "inline-flex" }}>
              <Icon name={item.icon} size={16} />
              {!!badge && <span className="r-nav__badge">{badge > 9 ? "9+" : badge}</span>}
            </span>
            <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.label}</span>
          </button>
        );
      })}
    </div>
  );

  if (!fixed) return bar;
  return (
    <nav
      style={{
        position: "fixed",
        insetInline: 0,
        bottom: 0,
        zIndex: 30,
        display: "flex",
        justifyContent: "center",
        padding: "16px 16px calc(env(safe-area-inset-bottom) + 14px)",
      }}
    >
      {bar}
    </nav>
  );
}
