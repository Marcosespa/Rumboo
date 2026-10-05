import React from "react";
import { Icon } from "../icons/Icon.jsx";

const PRESETS = {
  ok: { label: "Al día", icon: "CheckCircle2", cls: "r-pill--ok" },
  attention: { label: "Pendiente", icon: "Clock3", cls: "r-pill--attention" },
  critical: { label: "Urgente", icon: "TriangleAlert", cls: "r-pill--critical" },
  success: { label: "Pagado", icon: "CheckCircle2", cls: "r-pill--success" },
  warning: { label: "Por vencer", icon: "Clock3", cls: "r-pill--warning" },
  accent: { label: "Nuevo", icon: "Sparkles", cls: "r-pill--accent" },
};

/**
 * Vehicle/alert status pill. status presets carry the canonical Rumbo
 * labels ("Al día" / "Pendiente" / "Urgente"); children override.
 */
export function StatusPill({ status = "ok", solid = false, withIcon = false, children, className = "" }) {
  const preset = PRESETS[status] || PRESETS.ok;
  const cls =
    solid && status === "critical" ? "r-pill--critical-solid" : preset.cls;
  return (
    <span className={`r-pill ${cls} ${className}`.trim()}>
      {withIcon && <Icon name={preset.icon} size={12} />}
      {children || preset.label}
    </span>
  );
}
