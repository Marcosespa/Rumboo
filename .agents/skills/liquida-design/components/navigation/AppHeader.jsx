import React from "react";
import { IconButton } from "../buttons/IconButton.jsx";

/**
 * Brand chip: condor mark + "Rumbo" wordmark in a pill.
 */
export function BrandChip({ logoSrc, children = "Rumbo", className = "" }) {
  return (
    <span className={`r-brandchip ${className}`.trim()}>
      {logoSrc && (
        <img
          src={logoSrc}
          alt="Logo de Rumbo: cóndor andino"
          style={{ height: 24, width: 24, objectFit: "contain" }}
        />
      )}
      {children}
    </span>
  );
}

/**
 * Sticky app header: brand chip, page title (28px display), subtitle,
 * and 44px utility icon buttons on the right.
 */
export function AppHeader({
  title,
  subtitle,
  logoSrc,
  rightMeta,
  onRefresh,
  onLogout,
  className = "",
}) {
  return (
    <header
      className={className}
      style={{
        borderBottom: "1px solid rgba(231, 226, 215, 0.8)",
        background: "rgba(250, 248, 244, 0.9)",
        backdropFilter: "blur(24px)",
        WebkitBackdropFilter: "blur(24px)",
        padding: "20px 20px 16px",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16 }}>
        <div style={{ minWidth: 0 }}>
          <BrandChip logoSrc={logoSrc} />
          <h1
            style={{
              margin: "12px 0 0",
              fontSize: "var(--text-h1)",
              fontWeight: 600,
              letterSpacing: "var(--tracking-tight)",
              color: "var(--color-ink)",
              fontFamily: "var(--font-display)",
            }}
          >
            {title}
          </h1>
          {subtitle && (
            <p style={{ margin: "4px 0 0", maxWidth: 320, fontSize: "var(--text-base)", lineHeight: "var(--leading-relaxed)", color: "var(--color-mist)" }}>
              {subtitle}
            </p>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {rightMeta}
          {onRefresh && <IconButton icon="RefreshCw" label="Actualizar" onClick={onRefresh} />}
          {onLogout && <IconButton icon="LogOut" label="Salir" onClick={onLogout} />}
        </div>
      </div>
    </header>
  );
}
