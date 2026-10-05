/* @ds-bundle: {"format":3,"namespace":"RumboDesignSystem_252059","components":[{"name":"Button","sourcePath":"components/buttons/Button.jsx"},{"name":"IconButton","sourcePath":"components/buttons/IconButton.jsx"},{"name":"AlertCard","sourcePath":"components/feedback/AlertCard.jsx"},{"name":"EmptyState","sourcePath":"components/feedback/EmptyState.jsx"},{"name":"FilterChip","sourcePath":"components/feedback/FilterChip.jsx"},{"name":"StatusPill","sourcePath":"components/feedback/StatusPill.jsx"},{"name":"Field","sourcePath":"components/forms/Field.jsx"},{"name":"SegmentedControl","sourcePath":"components/forms/SegmentedControl.jsx"},{"name":"SelectField","sourcePath":"components/forms/SelectField.jsx"},{"name":"TextAreaField","sourcePath":"components/forms/TextAreaField.jsx"},{"name":"Icon","sourcePath":"components/icons/Icon.jsx"},{"name":"Metric","sourcePath":"components/layout/HeroPanel.jsx"},{"name":"HeroPanel","sourcePath":"components/layout/HeroPanel.jsx"},{"name":"ListRow","sourcePath":"components/layout/ListRow.jsx"},{"name":"SectionCard","sourcePath":"components/layout/SectionCard.jsx"},{"name":"StatTile","sourcePath":"components/layout/StatTile.jsx"},{"name":"BrandChip","sourcePath":"components/navigation/AppHeader.jsx"},{"name":"AppHeader","sourcePath":"components/navigation/AppHeader.jsx"},{"name":"BottomNav","sourcePath":"components/navigation/BottomNav.jsx"}],"sourceHashes":{"components/buttons/Button.jsx":"c23d30072c93","components/buttons/IconButton.jsx":"b1ee9c85b35c","components/feedback/AlertCard.jsx":"08dcbf9f7eb9","components/feedback/EmptyState.jsx":"476e0ba80c3a","components/feedback/FilterChip.jsx":"976dcca85516","components/feedback/StatusPill.jsx":"8dbb58e2e3a8","components/forms/Field.jsx":"51d5471bb201","components/forms/SegmentedControl.jsx":"0fb7c413f8da","components/forms/SelectField.jsx":"00d75ce946ce","components/forms/TextAreaField.jsx":"907b25865df8","components/icons/Icon.jsx":"94b4ef51d802","components/layout/HeroPanel.jsx":"2f6d36e950c4","components/layout/ListRow.jsx":"9e47d5c1bd06","components/layout/SectionCard.jsx":"efc7127c7808","components/layout/StatTile.jsx":"d1d3e60dad87","components/navigation/AppHeader.jsx":"f0d7a31270d5","components/navigation/BottomNav.jsx":"c9002ceecc9e","ui_kits/rumbo-app/AlertsScreen.jsx":"104d085f5f48","ui_kits/rumbo-app/CaptureScreen.jsx":"7e78772da48f","ui_kits/rumbo-app/DashboardScreen.jsx":"87472b8a49f8","ui_kits/rumbo-app/LoginScreen.jsx":"feaa33d1a0d5","ui_kits/rumbo-app/VehiclesScreen.jsx":"24db6dc174f6","ui_kits/rumbo-app/VerifyScreen.jsx":"3689b434e77e","ui_kits/rumbo-app/data.jsx":"da7887d49efe"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.RumboDesignSystem_252059 = window.RumboDesignSystem_252059 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/buttons/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Rumbo button. Mirrors fleteControl's Button.jsx variants plus an
 * `accent` (ámbar señal) variant reserved for the main camera CTA.
 */
function Button({
  variant = "primary",
  size,
  block = false,
  loading = false,
  as = "button",
  className = "",
  children,
  ...props
}) {
  const variantClass = variant === "lightGhost" ? "light-ghost" : variant;
  const cls = ["r-btn", `r-btn--${variantClass}`, size === "lg" ? "r-btn--lg" : "", block ? "r-btn--block" : "", className].filter(Boolean).join(" ");
  const Comp = as;
  return /*#__PURE__*/React.createElement(Comp, _extends({
    className: cls,
    disabled: loading || props.disabled
  }, props), loading ? /*#__PURE__*/React.createElement("span", {
    style: {
      display: "inline-flex",
      alignItems: "center",
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    className: "r-spinner"
  }), /*#__PURE__*/React.createElement("span", null, "Espera...")) : children);
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/buttons/Button.jsx", error: String((e && e.message) || e) }); }

// components/feedback/FilterChip.jsx
try { (() => {
/**
 * Round filter chip; active state is ink-filled.
 */
function FilterChip({
  active = false,
  onClick,
  children,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: `r-chip ${active ? "is-active" : ""} ${className}`.trim(),
    onClick: onClick
  }, children);
}
Object.assign(__ds_scope, { FilterChip });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/FilterChip.jsx", error: String((e && e.message) || e) }); }

// components/forms/Field.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Labeled text input. cloudSoft fill, line border; focus turns the
 * field paper-white with a primary border + soft ring.
 * Note: onChange receives the VALUE, not the event (matches product code).
 */
function Field({
  label,
  hint,
  className = "",
  onChange,
  ...props
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: className,
    style: {
      display: "block"
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    className: "r-label"
  }, label), /*#__PURE__*/React.createElement("input", _extends({
    className: "r-input",
    onChange: onChange ? event => onChange(event.target.value) : undefined
  }, props)), hint && /*#__PURE__*/React.createElement("span", {
    style: {
      display: "block",
      marginTop: 6,
      fontSize: "var(--text-sm)",
      color: "var(--color-mist)"
    }
  }, hint));
}
Object.assign(__ds_scope, { Field });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/Field.jsx", error: String((e && e.message) || e) }); }

// components/forms/SegmentedControl.jsx
try { (() => {
/**
 * Segmented control — cloudSoft track, active segment goes ink/paper.
 * Used for login/register toggle and document-type pickers.
 */
function SegmentedControl({
  options = [],
  value,
  onChange,
  block = false,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: `r-seg ${block ? "r-seg--block" : ""} ${className}`.trim(),
    role: "tablist"
  }, options.map(opt => {
    const o = typeof opt === "string" ? {
      value: opt,
      label: opt
    } : opt;
    const active = value === o.value;
    return /*#__PURE__*/React.createElement("button", {
      key: o.value,
      type: "button",
      role: "tab",
      "aria-selected": active,
      className: `r-seg__btn ${active ? "is-active" : ""}`.trim(),
      onClick: onChange ? () => onChange(o.value) : undefined
    }, o.label);
  }));
}
Object.assign(__ds_scope, { SegmentedControl });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/SegmentedControl.jsx", error: String((e && e.message) || e) }); }

// components/forms/SelectField.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Labeled select, same skin as Field. Options accept strings or
 * { value, label } objects.
 */
function SelectField({
  label,
  options = [],
  onChange,
  className = "",
  ...props
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: className,
    style: {
      display: "block"
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    className: "r-label"
  }, label), /*#__PURE__*/React.createElement("select", _extends({
    className: "r-input",
    onChange: onChange ? event => onChange(event.target.value) : undefined
  }, props), options.map(opt => {
    const o = typeof opt === "string" ? {
      value: opt,
      label: opt
    } : opt;
    return /*#__PURE__*/React.createElement("option", {
      key: o.value,
      value: o.value
    }, o.label);
  })));
}
Object.assign(__ds_scope, { SelectField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/SelectField.jsx", error: String((e && e.message) || e) }); }

// components/forms/TextAreaField.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Labeled multi-line input, same skin as Field.
 */
function TextAreaField({
  label,
  rows = 3,
  onChange,
  className = "",
  ...props
}) {
  return /*#__PURE__*/React.createElement("label", {
    className: className,
    style: {
      display: "block"
    }
  }, label && /*#__PURE__*/React.createElement("span", {
    className: "r-label"
  }, label), /*#__PURE__*/React.createElement("textarea", _extends({
    className: "r-input",
    rows: rows,
    onChange: onChange ? event => onChange(event.target.value) : undefined
  }, props)));
}
Object.assign(__ds_scope, { TextAreaField });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/forms/TextAreaField.jsx", error: String((e && e.message) || e) }); }

// components/icons/Icon.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Lucide icon adapter. Rumbo uses the Lucide icon set (the product code
 * imports lucide-react). Load the Lucide UMD bundle once per page:
 *   <script src="https://unpkg.com/lucide@0.469.0/dist/umd/lucide.min.js"></script>
 * then <Icon name="Camera" /> renders the real Lucide path data.
 */
function Icon({
  name,
  size = 16,
  strokeWidth = 2,
  color = "currentColor",
  style = {},
  ...props
}) {
  const registry = typeof window !== "undefined" && window.lucide && window.lucide.icons ? window.lucide.icons : null;
  const node = registry ? registry[name] : null;
  if (!node) {
    return /*#__PURE__*/React.createElement("span", {
      "aria-hidden": "true",
      style: {
        display: "inline-block",
        width: size,
        height: size,
        flex: "none",
        ...style
      }
    });
  }
  let kids = node;
  if (typeof node[0] === "string") kids = node[2] || [];
  return /*#__PURE__*/React.createElement("svg", _extends({
    xmlns: "http://www.w3.org/2000/svg",
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: color,
    strokeWidth: strokeWidth,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": "true",
    style: {
      flex: "none",
      ...style
    }
  }, props), kids.map((child, i) => {
    const tag = child[0];
    const attrs = child[1] || {};
    return React.createElement(tag, {
      ...attrs,
      key: i
    });
  }));
}
Object.assign(__ds_scope, { Icon });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/icons/Icon.jsx", error: String((e && e.message) || e) }); }

// components/buttons/IconButton.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * 44px square bordered icon button (header refresh / logout actions).
 */
function IconButton({
  icon,
  label,
  size = 16,
  className = "",
  ...props
}) {
  return /*#__PURE__*/React.createElement("button", _extends({
    type: "button",
    className: `r-iconbtn ${className}`.trim(),
    "aria-label": label,
    title: label
  }, props), /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: size
  }));
}
Object.assign(__ds_scope, { IconButton });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/buttons/IconButton.jsx", error: String((e && e.message) || e) }); }

// components/feedback/EmptyState.jsx
try { (() => {
/**
 * Dashed empty state with icon box and friendly guidance copy.
 */
function EmptyState({
  icon = "Camera",
  text,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: `r-subcard r-subcard--dashed ${className}`.trim()
  }, /*#__PURE__*/React.createElement("div", {
    className: "r-empty__icon"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 16
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "12px 0 0",
      fontSize: "var(--text-base)",
      lineHeight: "var(--leading-relaxed)",
      color: "var(--color-mist)"
    }
  }, text));
}
Object.assign(__ds_scope, { EmptyState });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/EmptyState.jsx", error: String((e && e.message) || e) }); }

// components/feedback/StatusPill.jsx
try { (() => {
const PRESETS = {
  ok: {
    label: "Al día",
    icon: "CheckCircle2",
    cls: "r-pill--ok"
  },
  attention: {
    label: "Pendiente",
    icon: "Clock3",
    cls: "r-pill--attention"
  },
  critical: {
    label: "Urgente",
    icon: "TriangleAlert",
    cls: "r-pill--critical"
  },
  success: {
    label: "Pagado",
    icon: "CheckCircle2",
    cls: "r-pill--success"
  },
  warning: {
    label: "Por vencer",
    icon: "Clock3",
    cls: "r-pill--warning"
  },
  accent: {
    label: "Nuevo",
    icon: "Sparkles",
    cls: "r-pill--accent"
  }
};

/**
 * Vehicle/alert status pill. status presets carry the canonical Rumbo
 * labels ("Al día" / "Pendiente" / "Urgente"); children override.
 */
function StatusPill({
  status = "ok",
  solid = false,
  withIcon = false,
  children,
  className = ""
}) {
  const preset = PRESETS[status] || PRESETS.ok;
  const cls = solid && status === "critical" ? "r-pill--critical-solid" : preset.cls;
  return /*#__PURE__*/React.createElement("span", {
    className: `r-pill ${cls} ${className}`.trim()
  }, withIcon && /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: preset.icon,
    size: 12
  }), children || preset.label);
}
Object.assign(__ds_scope, { StatusPill });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/StatusPill.jsx", error: String((e && e.message) || e) }); }

// components/feedback/AlertCard.jsx
try { (() => {
/**
 * Alert/receivable card: cloudSoft surface (error-tinted when critical),
 * title + detail + meta line, status pill, optional action row.
 */
function AlertCard({
  severity = "attention",
  title,
  detail,
  meta,
  pill = true,
  actions,
  className = ""
}) {
  const critical = severity === "critical";
  return /*#__PURE__*/React.createElement("div", {
    className: `r-subcard ${critical ? "r-subcard--error" : ""} ${className}`.trim()
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--text-base)",
      fontWeight: 600,
      color: "var(--color-ink)"
    }
  }, title), detail && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "4px 0 0",
      fontSize: "var(--text-base)",
      lineHeight: "var(--leading-relaxed)",
      color: "var(--color-mist)"
    }
  }, detail), meta && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "8px 0 0",
      fontSize: "var(--text-xs)",
      textTransform: "uppercase",
      letterSpacing: "0.16em",
      color: "var(--color-mist)"
    }
  }, meta)), pill && /*#__PURE__*/React.createElement(__ds_scope.StatusPill, {
    status: critical ? "critical" : "attention",
    solid: critical
  }, critical ? "Urgente" : "Atención")), actions && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 16,
      display: "grid",
      gap: 8,
      gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))"
    }
  }, actions));
}
Object.assign(__ds_scope, { AlertCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/feedback/AlertCard.jsx", error: String((e && e.message) || e) }); }

// components/layout/HeroPanel.jsx
try { (() => {
function Metric({
  label,
  value
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "r-metric"
  }, /*#__PURE__*/React.createElement("p", {
    className: "r-metric__label"
  }, label), /*#__PURE__*/React.createElement("p", {
    className: "r-metric__value"
  }, value));
}

/**
 * Hero stat panel — the dark "answer" block at the top of each screen
 * (ink on Panel/Alertas, primary on Vehículos). Holds the protagonist
 * figure, a 3-up metric grid and light/lightGhost action buttons.
 */
function HeroPanel({
  overline,
  figure,
  caption,
  tone = "ink",
  metrics = [],
  actions,
  children,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: `r-hero ${tone === "primary" ? "r-hero--primary" : ""} ${className}`.trim()
  }, overline && /*#__PURE__*/React.createElement("p", {
    className: "r-overline"
  }, overline), figure && /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: "12px 0 0",
      fontSize: "var(--text-figure)",
      fontWeight: 600,
      letterSpacing: "var(--tracking-tight)",
      fontFamily: "var(--font-display)"
    }
  }, figure), caption && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "8px 0 0",
      maxWidth: "20rem",
      fontSize: "var(--text-base)",
      lineHeight: "var(--leading-relaxed)",
      opacity: 0.7
    }
  }, caption), metrics.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 24,
      display: "grid",
      gridTemplateColumns: `repeat(${Math.min(metrics.length, 4)}, 1fr)`,
      gap: 12
    }
  }, metrics.map(m => /*#__PURE__*/React.createElement(Metric, {
    key: m.label,
    label: m.label,
    value: m.value
  }))), actions && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 24,
      display: "grid",
      gap: 12,
      gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))"
    }
  }, actions), children);
}
Object.assign(__ds_scope, { Metric, HeroPanel });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/HeroPanel.jsx", error: String((e && e.message) || e) }); }

// components/layout/ListRow.jsx
try { (() => {
/**
 * Movement list row: title + meta on the left, signed amount on the right.
 * Amount color: expense = error (with minus), income/receivable = primary.
 */
function ListRow({
  title,
  meta,
  amount,
  tone = "neutral",
  className = ""
}) {
  const color = tone === "expense" ? "var(--color-error)" : tone === "income" ? "var(--color-primary)" : "var(--color-ink)";
  return /*#__PURE__*/React.createElement("div", {
    className: `r-listrow ${className}`.trim()
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: "var(--text-base)",
      fontWeight: 600,
      color: "var(--color-ink)",
      overflow: "hidden",
      textOverflow: "ellipsis",
      whiteSpace: "nowrap"
    }
  }, title), meta && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "4px 0 0",
      fontSize: "var(--text-base)",
      color: "var(--color-mist)"
    }
  }, meta)), /*#__PURE__*/React.createElement("span", {
    style: {
      flex: "none",
      fontSize: "var(--text-base)",
      fontWeight: 600,
      color
    }
  }, tone === "expense" ? "-" : "", amount));
}
Object.assign(__ds_scope, { ListRow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/ListRow.jsx", error: String((e && e.message) || e) }); }

// components/layout/SectionCard.jsx
try { (() => {
/**
 * Section card — 28px radius paper panel with title/subtitle header
 * and optional right-aligned action. Direct port of SectionCard.jsx.
 */
function SectionCard({
  title,
  subtitle,
  action,
  children,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: `r-card ${className}`.trim()
  }, (title || subtitle || action) && /*#__PURE__*/React.createElement("div", {
    style: {
      marginBottom: 16,
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, title && /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      fontSize: "var(--text-body)",
      fontWeight: 600,
      letterSpacing: "var(--tracking-tight)",
      color: "var(--color-ink)"
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "4px 0 0",
      fontSize: "var(--text-base)",
      lineHeight: "var(--leading-relaxed)",
      color: "var(--color-mist)"
    }
  }, subtitle)), action), children);
}
Object.assign(__ds_scope, { SectionCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/SectionCard.jsx", error: String((e && e.message) || e) }); }

// components/layout/StatTile.jsx
try { (() => {
/**
 * Light stat tile with a primary icon + title head and a mist value line.
 * (VehicleStat / MiniStat in the product code.)
 */
function StatTile({
  icon,
  title,
  value,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: `r-stattile ${className}`.trim()
  }, /*#__PURE__*/React.createElement("div", {
    className: "r-stattile__head"
  }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
    name: icon,
    size: 16
  }), /*#__PURE__*/React.createElement("p", {
    className: "r-stattile__title"
  }, title)), /*#__PURE__*/React.createElement("p", {
    className: "r-stattile__value"
  }, value));
}
Object.assign(__ds_scope, { StatTile });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/StatTile.jsx", error: String((e && e.message) || e) }); }

// components/navigation/AppHeader.jsx
try { (() => {
/**
 * Brand chip: condor mark + "Rumbo" wordmark in a pill.
 */
function BrandChip({
  logoSrc,
  children = "Rumbo",
  className = ""
}) {
  return /*#__PURE__*/React.createElement("span", {
    className: `r-brandchip ${className}`.trim()
  }, logoSrc && /*#__PURE__*/React.createElement("img", {
    src: logoSrc,
    alt: "Logo de Rumbo: c\xF3ndor andino",
    style: {
      height: 24,
      width: 24,
      objectFit: "contain"
    }
  }), children);
}

/**
 * Sticky app header: brand chip, page title (28px display), subtitle,
 * and 44px utility icon buttons on the right.
 */
function AppHeader({
  title,
  subtitle,
  logoSrc,
  rightMeta,
  onRefresh,
  onLogout,
  className = ""
}) {
  return /*#__PURE__*/React.createElement("header", {
    className: className,
    style: {
      borderBottom: "1px solid rgba(231, 226, 215, 0.8)",
      background: "rgba(250, 248, 244, 0.9)",
      backdropFilter: "blur(24px)",
      WebkitBackdropFilter: "blur(24px)",
      padding: "20px 20px 16px"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement(BrandChip, {
    logoSrc: logoSrc
  }), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: "12px 0 0",
      fontSize: "var(--text-h1)",
      fontWeight: 600,
      letterSpacing: "var(--tracking-tight)",
      color: "var(--color-ink)",
      fontFamily: "var(--font-display)"
    }
  }, title), subtitle && /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "4px 0 0",
      maxWidth: 320,
      fontSize: "var(--text-base)",
      lineHeight: "var(--leading-relaxed)",
      color: "var(--color-mist)"
    }
  }, subtitle)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8
    }
  }, rightMeta, onRefresh && /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "RefreshCw",
    label: "Actualizar",
    onClick: onRefresh
  }), onLogout && /*#__PURE__*/React.createElement(__ds_scope.IconButton, {
    icon: "LogOut",
    label: "Salir",
    onClick: onLogout
  }))));
}
Object.assign(__ds_scope, { BrandChip, AppHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/AppHeader.jsx", error: String((e && e.message) || e) }); }

// components/navigation/BottomNav.jsx
try { (() => {
const DEFAULT_ITEMS = [{
  id: "dashboard",
  label: "Panel",
  icon: "ChartColumn"
}, {
  id: "vehicles",
  label: "Vehículos",
  icon: "CarFront"
}, {
  id: "alerts",
  label: "Alertas",
  icon: "Bell"
}, {
  id: "capture",
  label: "Foto",
  icon: "Camera"
}, {
  id: "verify",
  label: "Nuevo",
  icon: "PlusCircle"
}];

/**
 * Floating bottom navigation — pill bar with ink-filled active item and
 * an error badge on Alertas. Labels are always visible.
 */
function BottomNav({
  items = DEFAULT_ITEMS,
  active,
  onSelect,
  badges = {},
  fixed = false,
  className = ""
}) {
  const bar = /*#__PURE__*/React.createElement("div", {
    className: `r-navbar ${className}`.trim(),
    style: {
      width: "100%",
      maxWidth: "var(--content-max)"
    }
  }, items.map(item => {
    const badge = badges[item.id] || 0;
    return /*#__PURE__*/React.createElement("button", {
      key: item.id,
      type: "button",
      className: `r-nav__item ${active === item.id ? "is-active" : ""}`.trim(),
      onClick: onSelect ? () => onSelect(item.id) : undefined
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        position: "relative",
        display: "inline-flex"
      }
    }, /*#__PURE__*/React.createElement(__ds_scope.Icon, {
      name: item.icon,
      size: 16
    }), !!badge && /*#__PURE__*/React.createElement("span", {
      className: "r-nav__badge"
    }, badge > 9 ? "9+" : badge)), /*#__PURE__*/React.createElement("span", {
      style: {
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap"
      }
    }, item.label));
  }));
  if (!fixed) return bar;
  return /*#__PURE__*/React.createElement("nav", {
    style: {
      position: "fixed",
      insetInline: 0,
      bottom: 0,
      zIndex: 30,
      display: "flex",
      justifyContent: "center",
      padding: "16px 16px calc(env(safe-area-inset-bottom) + 14px)"
    }
  }, bar);
}
Object.assign(__ds_scope, { BottomNav });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/BottomNav.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/AlertsScreen.jsx
try { (() => {
// Rumbo UI kit — Alerts (Alertas)
function AlertsScreen({
  go
}) {
  const DS = window.RumboDesignSystem_252059;
  const {
    AppHeader,
    FilterChip,
    AlertCard,
    Button,
    Icon,
    EmptyState
  } = DS;
  const d = window.RUMBO_DATA;
  const [filter, setFilter] = React.useState("all");
  const [resolved, setResolved] = React.useState([]);
  const visible = d.alerts.filter(a => !resolved.includes(a.title) && (filter === "all" || a.severity === filter));
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Alertas"
  }, /*#__PURE__*/React.createElement(AppHeader, {
    title: "Alertas",
    subtitle: "Lo que necesita atenci\xF3n, de lo m\xE1s urgente a lo menos.",
    logoSrc: "../../assets/logos/condor-sm.png",
    onRefresh: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "16px 20px 0",
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 8,
      flexWrap: "wrap"
    }
  }, /*#__PURE__*/React.createElement(FilterChip, {
    active: filter === "all",
    onClick: () => setFilter("all")
  }, "Todas"), /*#__PURE__*/React.createElement(FilterChip, {
    active: filter === "critical",
    onClick: () => setFilter("critical")
  }, "Urgentes"), /*#__PURE__*/React.createElement(FilterChip, {
    active: filter === "attention",
    onClick: () => setFilter("attention")
  }, "Atenci\xF3n")), visible.length === 0 ? /*#__PURE__*/React.createElement(EmptyState, {
    icon: "CheckCircle2",
    text: "Nada pendiente por aqu\xED. Todo al d\xEDa."
  }) : /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 12
    }
  }, visible.map(a => /*#__PURE__*/React.createElement(AlertCard, {
    key: a.title,
    severity: a.severity,
    title: a.title,
    detail: a.detail,
    meta: a.meta,
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "secondary",
      onClick: () => go("vehicles")
    }, /*#__PURE__*/React.createElement(Icon, {
      name: "CarFront"
    }), " Ver veh\xEDculo"), /*#__PURE__*/React.createElement(Button, {
      onClick: () => setResolved([...resolved, a.title])
    }, /*#__PURE__*/React.createElement(Icon, {
      name: "CheckCircle2"
    }), " Resolver"))
  })))));
}
window.RumboAlertsScreen = AlertsScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/AlertsScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/CaptureScreen.jsx
try { (() => {
// Rumbo UI kit — Capture (Foto)
function CaptureScreen({
  go
}) {
  const DS = window.RumboDesignSystem_252059;
  const {
    AppHeader,
    SegmentedControl,
    Button,
    Icon,
    EmptyState
  } = DS;
  const [kind, setKind] = React.useState("gasto");
  const hints = {
    gasto: "Recibos de gasolina, peajes, repuestos o mantenimiento.",
    cobro: "Remesas, cuentas de cobro o comprobantes de pago.",
    vehiculo: "SOAT, tecnomecánica u otros documentos del vehículo."
  };
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Foto"
  }, /*#__PURE__*/React.createElement(AppHeader, {
    title: "Toma una foto",
    subtitle: "Rumbo lee el documento y arma el registro por ti.",
    logoSrc: "../../assets/logos/condor-sm.png"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "16px 20px 0",
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "r-card"
  }, /*#__PURE__*/React.createElement("p", {
    className: "r-label",
    style: {
      marginBottom: 8
    }
  }, "\xBFQu\xE9 vas a subir?"), /*#__PURE__*/React.createElement(SegmentedControl, {
    block: true,
    options: [{
      value: "gasto",
      label: "Gasto"
    }, {
      value: "cobro",
      label: "Cobro"
    }, {
      value: "vehiculo",
      label: "Vehículo"
    }],
    value: kind,
    onChange: setKind
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "12px 0 0",
      fontSize: 14,
      lineHeight: 1.6,
      color: "var(--color-mist)"
    }
  }, hints[kind]), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 20,
      display: "flex",
      flexDirection: "column",
      gap: 12
    }
  }, /*#__PURE__*/React.createElement(Button, {
    variant: "accent",
    size: "lg",
    block: true,
    onClick: () => go("verify")
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "Camera",
    size: 18
  }), " Tomar foto"), /*#__PURE__*/React.createElement(Button, {
    variant: "secondary",
    block: true,
    onClick: () => go("verify")
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "FileUp"
  }), " Subir desde el tel\xE9fono"))), /*#__PURE__*/React.createElement("div", {
    className: "r-card"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 8,
      color: "var(--color-primary)"
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "Sparkles",
    size: 16
  }), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 14,
      fontWeight: 600,
      color: "var(--color-ink)"
    }
  }, "As\xED funciona")), /*#__PURE__*/React.createElement("ol", {
    style: {
      margin: "12px 0 0",
      padding: "0 0 0 20px",
      display: "flex",
      flexDirection: "column",
      gap: 8,
      fontSize: 14,
      lineHeight: 1.6,
      color: "var(--color-mist)"
    }
  }, /*#__PURE__*/React.createElement("li", null, "Toma la foto con buena luz, que se lean los n\xFAmeros."), /*#__PURE__*/React.createElement("li", null, "Rumbo saca monto, fecha y de qu\xE9 es el documento."), /*#__PURE__*/React.createElement("li", null, "T\xFA revisas, corriges si hace falta y guardas."))), /*#__PURE__*/React.createElement(EmptyState, {
    icon: "Camera",
    text: "Las fotos que subas hoy aparecer\xE1n aqu\xED mientras se procesan."
  })));
}
window.RumboCaptureScreen = CaptureScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/CaptureScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/DashboardScreen.jsx
try { (() => {
// Rumbo UI kit — Dashboard (Panel)
function DashboardScreen({
  go
}) {
  const DS = window.RumboDesignSystem_252059;
  const {
    AppHeader,
    HeroPanel,
    SectionCard,
    ListRow,
    AlertCard,
    Button,
    Icon
  } = DS;
  const d = window.RUMBO_DATA;
  const f = window.formatCOP;
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Panel"
  }, /*#__PURE__*/React.createElement(AppHeader, {
    title: `Hola, ${d.user}`,
    subtitle: "Revisa caja, cobros y estado del veh\xEDculo.",
    logoSrc: "../../assets/logos/condor-sm.png",
    rightMeta: /*#__PURE__*/React.createElement("span", {
      className: "r-pill",
      style: {
        border: "1px solid var(--color-line)",
        background: "var(--color-cloud-soft)",
        color: "var(--color-mist)"
      }
    }, d.month),
    onRefresh: () => {},
    onLogout: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "16px 20px 0",
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(HeroPanel, {
    overline: "Este mes",
    figure: f(d.cash.left),
    caption: "Lo que realmente te queda despu\xE9s de ingresos y gastos.",
    metrics: [{
      label: "Entró",
      value: f(d.cash.income)
    }, {
      label: "Salió",
      value: f(d.cash.expense)
    }, {
      label: "Te deben",
      value: f(d.cash.owed)
    }],
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Button, {
      variant: "light",
      onClick: () => go("capture")
    }, /*#__PURE__*/React.createElement(Icon, {
      name: "Camera"
    }), " Tomar foto"), /*#__PURE__*/React.createElement(Button, {
      variant: "lightGhost",
      onClick: () => go("verify")
    }, /*#__PURE__*/React.createElement(Icon, {
      name: "Plus"
    }), " Agregar sin foto"))
  }), /*#__PURE__*/React.createElement(SectionCard, {
    title: "Alertas del negocio",
    subtitle: "Cobros y recordatorios que merecen atenci\xF3n.",
    action: /*#__PURE__*/React.createElement("button", {
      className: "r-btn r-btn--ghost",
      onClick: () => go("alerts"),
      style: {
        padding: "8px 12px",
        minHeight: 0
      }
    }, "Ver todas ", /*#__PURE__*/React.createElement(Icon, {
      name: "ArrowRight",
      size: 14
    }))
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 12
    }
  }, d.receivables.map(r => /*#__PURE__*/React.createElement(AlertCard, {
    key: r.title,
    severity: r.severity,
    title: r.title,
    detail: r.detail,
    meta: r.meta
  })))), /*#__PURE__*/React.createElement(SectionCard, {
    title: "\xDAltimos movimientos",
    subtitle: "Lo \xFAltimo que registraste con foto o a mano."
  }, d.movements.map(m => /*#__PURE__*/React.createElement(ListRow, {
    key: m.title,
    title: m.title,
    meta: m.meta,
    amount: f(m.amount),
    tone: m.tone
  })))));
}
window.RumboDashboardScreen = DashboardScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/DashboardScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/LoginScreen.jsx
try { (() => {
// Rumbo UI kit — Login screen
function LoginScreen({
  onEnter
}) {
  const DS = window.RumboDesignSystem_252059;
  const {
    Button,
    Field,
    SegmentedControl,
    Icon
  } = DS;
  const [mode, setMode] = React.useState("login");
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Login",
    style: {
      minHeight: "100%",
      display: "flex",
      flexDirection: "column",
      padding: "40px 20px 32px",
      boxSizing: "border-box"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      textAlign: "center"
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: "../../assets/logos/condor.png",
    alt: "Logo de Rumbo: c\xF3ndor andino con collar \xE1mbar",
    style: {
      height: 96,
      objectFit: "contain"
    }
  }), /*#__PURE__*/React.createElement("h1", {
    style: {
      margin: "16px 0 0",
      fontFamily: "var(--font-display)",
      fontSize: 34,
      fontWeight: 600,
      letterSpacing: "-0.01em",
      color: "var(--color-ink)"
    }
  }, "Rumbo"), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "8px 0 0",
      fontSize: 15,
      lineHeight: 1.5,
      color: "var(--color-mist)"
    }
  }, "Tu cami\xF3n y tu plata, al d\xEDa.")), /*#__PURE__*/React.createElement("div", {
    className: "r-card",
    style: {
      marginTop: 28
    }
  }, /*#__PURE__*/React.createElement(SegmentedControl, {
    block: true,
    options: [{
      value: "login",
      label: "Entrar"
    }, {
      value: "register",
      label: "Crear cuenta"
    }],
    value: mode,
    onChange: setMode
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 20,
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, mode === "register" && /*#__PURE__*/React.createElement(Field, {
    label: "Nombre",
    placeholder: "Ej. Marcos Espinosa"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Usuario o correo",
    placeholder: "Ej. marcos o tu correo"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Contrase\xF1a",
    type: "password",
    placeholder: mode === "register" ? "Mínimo 8 caracteres" : "Tu contraseña"
  }), /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    block: true,
    onClick: onEnter
  }, mode === "login" ? "Entrar al panel" : "Crear mi cuenta", " ", /*#__PURE__*/React.createElement(Icon, {
    name: "ArrowRight"
  })))), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 24,
      display: "flex",
      flexDirection: "column",
      gap: 12
    }
  }, [{
    icon: "Camera",
    text: "Toma una foto del recibo y Rumbo lo registra solo."
  }, {
    icon: "CircleDollarSign",
    text: "Mira cuánto te queda este mes, sin cuentas raras."
  }, {
    icon: "WalletCards",
    text: "Controla quién te debe y qué documentos vencen."
  }].map(item => /*#__PURE__*/React.createElement("div", {
    key: item.icon,
    style: {
      display: "flex",
      alignItems: "center",
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: "flex",
      width: 36,
      height: 36,
      alignItems: "center",
      justifyContent: "center",
      borderRadius: 14,
      background: "var(--color-primary-subtle)",
      color: "var(--color-primary)",
      flex: "none"
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: item.icon,
    size: 16
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 14,
      lineHeight: 1.5,
      color: "var(--color-stone)"
    }
  }, item.text)))));
}
window.RumboLoginScreen = LoginScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/LoginScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/VehiclesScreen.jsx
try { (() => {
// Rumbo UI kit — Vehicles (Vehículos)
function VehiclesScreen({
  go
}) {
  const DS = window.RumboDesignSystem_252059;
  const {
    AppHeader,
    HeroPanel,
    StatTile,
    StatusPill,
    Button,
    Icon
  } = DS;
  const d = window.RUMBO_DATA;
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Veh\xEDculos"
  }, /*#__PURE__*/React.createElement(AppHeader, {
    title: "Tus veh\xEDculos",
    subtitle: "Documentos, mantenimiento y alertas de cada uno.",
    logoSrc: "../../assets/logos/condor-sm.png",
    onRefresh: () => {}
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "16px 20px 0",
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(HeroPanel, {
    tone: "primary",
    overline: "Flota",
    figure: "3 veh\xEDculos",
    caption: "1 urgente, 1 pendiente y 1 al d\xEDa.",
    actions: /*#__PURE__*/React.createElement(Button, {
      variant: "light",
      onClick: () => go("capture")
    }, /*#__PURE__*/React.createElement(Icon, {
      name: "Camera"
    }), " Subir documento")
  }), d.vehicles.map(v => /*#__PURE__*/React.createElement("div", {
    key: v.plate,
    className: "r-card"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "flex-start",
      justifyContent: "space-between",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h2", {
    style: {
      margin: 0,
      fontSize: 18,
      fontWeight: 600,
      letterSpacing: "-0.01em",
      color: "var(--color-ink)",
      fontFamily: "var(--font-display)"
    }
  }, v.name), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: "4px 0 0",
      fontSize: 14,
      color: "var(--color-mist)"
    }
  }, v.kind, " \xB7 ", v.plate)), /*#__PURE__*/React.createElement(StatusPill, {
    status: v.status,
    solid: v.status === "critical",
    withIcon: true
  }, v.statusLabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 16,
      display: "grid",
      gridTemplateColumns: "repeat(3, 1fr)",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement(StatTile, {
    icon: "ShieldCheck",
    title: "Docs",
    value: v.docs
  }), /*#__PURE__*/React.createElement(StatTile, {
    icon: "Wrench",
    title: "Mantto.",
    value: v.maint
  }), /*#__PURE__*/React.createElement(StatTile, {
    icon: "TriangleAlert",
    title: "Alertas",
    value: v.alerts
  })), /*#__PURE__*/React.createElement("button", {
    className: "r-btn r-btn--ghost",
    style: {
      marginTop: 12,
      padding: "8px 12px",
      minHeight: 0
    },
    onClick: () => go("alerts")
  }, "Ver detalle ", /*#__PURE__*/React.createElement(Icon, {
    name: "ArrowRight",
    size: 14
  }))))));
}
window.RumboVehiclesScreen = VehiclesScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/VehiclesScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/VerifyScreen.jsx
try { (() => {
// Rumbo UI kit — Verify (Nuevo / revisar registro)
function VerifyScreen({
  go
}) {
  const DS = window.RumboDesignSystem_252059;
  const {
    AppHeader,
    Field,
    SelectField,
    TextAreaField,
    SegmentedControl,
    Button,
    Icon,
    StatusPill
  } = DS;
  const [kind, setKind] = React.useState("gasto");
  const [saved, setSaved] = React.useState(false);
  return /*#__PURE__*/React.createElement("div", {
    "data-screen-label": "Nuevo"
  }, /*#__PURE__*/React.createElement(AppHeader, {
    title: "Revisa y guarda",
    subtitle: "Esto fue lo que Rumbo ley\xF3 de tu foto.",
    logoSrc: "../../assets/logos/condor-sm.png"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "16px 20px 0",
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "r-subcard",
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: 12
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      alignItems: "center",
      gap: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      display: "flex",
      width: 36,
      height: 36,
      alignItems: "center",
      justifyContent: "center",
      borderRadius: 14,
      background: "var(--color-accent-subtle)",
      color: "var(--color-accent-dark)",
      flex: "none"
    }
  }, /*#__PURE__*/React.createElement(Icon, {
    name: "Sparkles",
    size: 16
  })), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontSize: 14,
      lineHeight: 1.5,
      color: "var(--color-stone)"
    }
  }, "Le\xEDmos casi todo. Revisa el monto antes de guardar.")), /*#__PURE__*/React.createElement(StatusPill, {
    status: "warning"
  }, "Revisar")), /*#__PURE__*/React.createElement("div", {
    className: "r-card",
    style: {
      display: "flex",
      flexDirection: "column",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("p", {
    className: "r-label",
    style: {
      marginBottom: 8
    }
  }, "Tipo de registro"), /*#__PURE__*/React.createElement(SegmentedControl, {
    block: true,
    options: [{
      value: "gasto",
      label: "Gasto"
    }, {
      value: "cobro",
      label: "Cobro"
    }, {
      value: "vehiculo",
      label: "Vehículo"
    }],
    value: kind,
    onChange: setKind
  })), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(Field, {
    label: "Monto",
    defaultValue: "$ 180.000"
  }), /*#__PURE__*/React.createElement(Field, {
    label: "Fecha",
    defaultValue: "10 jun 2026"
  })), /*#__PURE__*/React.createElement(Field, {
    label: "\xBFDe qu\xE9 es?",
    defaultValue: "Estaci\xF3n Terpel La 80"
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      gap: 16
    }
  }, /*#__PURE__*/React.createElement(SelectField, {
    label: "Categor\xEDa",
    options: ["Gasolina", "Peajes", "Mantenimiento", "Repuestos", "Otro"]
  }), /*#__PURE__*/React.createElement(SelectField, {
    label: "Veh\xEDculo",
    options: [{
      value: "1",
      label: "Turbo Azul · WLN 482"
    }, {
      value: "2",
      label: "La Mula · SKT 911"
    }, {
      value: "",
      label: "Sin vehículo"
    }]
  })), /*#__PURE__*/React.createElement(TextAreaField, {
    label: "Nota (opcional)",
    placeholder: "Ej. Tanqueada completa para el viaje a Medell\xEDn."
  }), /*#__PURE__*/React.createElement(Button, {
    size: "lg",
    block: true,
    onClick: () => {
      setSaved(true);
      setTimeout(() => go("dashboard"), 900);
    }
  }, saved ? /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Icon, {
    name: "CheckCircle2"
  }), " Guardado") : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(Icon, {
    name: "CheckCircle2"
  }), " Guardar registro")))));
}
window.RumboVerifyScreen = VerifyScreen;
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/VerifyScreen.jsx", error: String((e && e.message) || e) }); }

// ui_kits/rumbo-app/data.jsx
try { (() => {
// Rumbo UI kit — shared fake data (matches product copy & es-CO formatting)
const formatCOP = n => "$ " + new Intl.NumberFormat("es-CO", {
  maximumFractionDigits: 0
}).format(n);
const RUMBO_DATA = {
  user: "Marcos",
  month: "junio 2026",
  cash: {
    left: 1250000,
    income: 3180000,
    expense: 1930000,
    owed: 860000
  },
  movements: [{
    title: "Remesa Coordinadora",
    meta: "Flete · 11 jun",
    amount: 450000,
    tone: "income"
  }, {
    title: "Estación Terpel La 80",
    meta: "Gasolina · 10 jun",
    amount: 180000,
    tone: "expense"
  }, {
    title: "Peaje Siberia",
    meta: "Peajes · 10 jun",
    amount: 13800,
    tone: "expense"
  }, {
    title: "Viaje Funza – Medellín",
    meta: "Flete · 8 jun",
    amount: 920000,
    tone: "income"
  }, {
    title: "Cambio de aceite",
    meta: "Mantenimiento · 6 jun",
    amount: 145000,
    tone: "expense"
  }],
  receivables: [{
    title: "Transportes La Sabana",
    detail: "Te deben $ 560.000 desde hace 12 días.",
    meta: "cobro · vence 15 jun",
    severity: "critical"
  }, {
    title: "Distribuidora El Triunfo",
    detail: "Te deben $ 300.000. Acordaron pagar esta semana.",
    meta: "cobro · vence 20 jun",
    severity: "attention"
  }],
  vehicles: [{
    name: "Turbo Azul",
    plate: "WLN 482",
    kind: "Turbo 4.5 t",
    status: "critical",
    statusLabel: "Urgente",
    docs: "SOAT vencido",
    maint: "Aceite al día",
    alerts: "2 activas"
  }, {
    name: "La Mula",
    plate: "SKT 911",
    kind: "Camión sencillo",
    status: "attention",
    statusLabel: "Pendiente",
    docs: "Tecno vence 28 jun",
    maint: "Frenos en 1.200 km",
    alerts: "1 activa"
  }, {
    name: "Moto Cargo",
    plate: "JDR 23F",
    kind: "Motocarro",
    status: "ok",
    statusLabel: "Al día",
    docs: "Todo vigente",
    maint: "Al día",
    alerts: "Sin alertas"
  }],
  alerts: [{
    title: "SOAT vencido — Turbo Azul",
    detail: "Venció el 2 de junio. Renuévalo para evitar multas y poder trabajar tranquilo.",
    meta: "documento · turbo azul",
    severity: "critical"
  }, {
    title: "Cobro vencido — Transportes La Sabana",
    detail: "Te deben $ 560.000 desde hace 12 días. Envía recordatorio o llama.",
    meta: "cartera · 12 días",
    severity: "critical"
  }, {
    title: "Tecnomecánica por vencer — La Mula",
    detail: "Vence el 28 de junio. Agenda la revisión esta semana.",
    meta: "documento · vence 28 jun",
    severity: "attention"
  }, {
    title: "Cambio de frenos — La Mula",
    detail: "Faltan unos 1.200 km según tu último registro.",
    meta: "mantenimiento · 1.200 km",
    severity: "attention"
  }]
};
Object.assign(window, {
  RUMBO_DATA,
  formatCOP
});
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/rumbo-app/data.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Button = __ds_scope.Button;

__ds_ns.IconButton = __ds_scope.IconButton;

__ds_ns.AlertCard = __ds_scope.AlertCard;

__ds_ns.EmptyState = __ds_scope.EmptyState;

__ds_ns.FilterChip = __ds_scope.FilterChip;

__ds_ns.StatusPill = __ds_scope.StatusPill;

__ds_ns.Field = __ds_scope.Field;

__ds_ns.SegmentedControl = __ds_scope.SegmentedControl;

__ds_ns.SelectField = __ds_scope.SelectField;

__ds_ns.TextAreaField = __ds_scope.TextAreaField;

__ds_ns.Icon = __ds_scope.Icon;

__ds_ns.Metric = __ds_scope.Metric;

__ds_ns.HeroPanel = __ds_scope.HeroPanel;

__ds_ns.ListRow = __ds_scope.ListRow;

__ds_ns.SectionCard = __ds_scope.SectionCard;

__ds_ns.StatTile = __ds_scope.StatTile;

__ds_ns.BrandChip = __ds_scope.BrandChip;

__ds_ns.AppHeader = __ds_scope.AppHeader;

__ds_ns.BottomNav = __ds_scope.BottomNav;

})();
