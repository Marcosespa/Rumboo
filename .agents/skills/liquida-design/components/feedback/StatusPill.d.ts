/**
 * Status pill with the canonical Rumbo state labels.
 */
export interface StatusPillProps {
  /**
   * ok="Al día" (paper/mist) · attention="Pendiente" (primary subtle) ·
   * critical="Urgente" (error subtle) · success · warning · accent.
   * @default "ok"
   */
  status?: "ok" | "attention" | "critical" | "success" | "warning" | "accent";
  /** critical only: solid error background with paper text. @default false */
  solid?: boolean;
  /** Prefix the preset Lucide icon (states = color + icon + text). @default false */
  withIcon?: boolean;
  /** Custom label; defaults to the canonical Spanish label */
  children?: React.ReactNode;
  className?: string;
}
export declare function StatusPill(props: StatusPillProps): JSX.Element;
