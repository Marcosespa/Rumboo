/** Light stat tile: primary icon + title, mist value. Used in 3-up grids inside vehicle cards. */
export interface StatTileProps {
  /** Lucide icon name, e.g. "ShieldCheck", "Wrench", "Fuel" */
  icon: string;
  title: string;
  value: string;
  className?: string;
}
export declare function StatTile(props: StatTileProps): JSX.Element;
