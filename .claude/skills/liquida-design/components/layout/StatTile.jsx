import React from "react";
import { Icon } from "../icons/Icon.jsx";

/**
 * Light stat tile with a primary icon + title head and a mist value line.
 * (VehicleStat / MiniStat in the product code.)
 */
export function StatTile({ icon, title, value, className = "" }) {
  return (
    <div className={`r-stattile ${className}`.trim()}>
      <div className="r-stattile__head">
        <Icon name={icon} size={16} />
        <p className="r-stattile__title">{title}</p>
      </div>
      <p className="r-stattile__value">{value}</p>
    </div>
  );
}
