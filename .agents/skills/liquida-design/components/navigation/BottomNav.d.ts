/**
 * Floating bottom navigation bar (Panel · Vehículos · Alertas · Foto · Nuevo).
 */
export interface BottomNavProps {
  /** Defaults to the five Rumbo destinations */
  items?: Array<{ id: string; label: string; icon: string }>;
  /** id of the active destination */
  active?: string;
  onSelect?: (id: string) => void;
  /** Numeric badges keyed by item id, e.g. { alerts: 3 } */
  badges?: Record<string, number>;
  /** Render fixed to the viewport bottom. @default false */
  fixed?: boolean;
  className?: string;
}
export declare function BottomNav(props: BottomNavProps): JSX.Element;
