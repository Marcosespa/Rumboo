/**
 * Dark hero stat panel that answers the screen's one question.
 */
export interface HeroPanelProps {
  /** Uppercase tracking label, e.g. "DASHBOARD" */
  overline?: string;
  /** Protagonist figure at 38px, e.g. "$ 1.250.000" */
  figure?: string;
  /** One-line explanation under the figure */
  caption?: string;
  /** ink (Panel, Alertas) or primary blue (Vehículos). @default "ink" */
  tone?: "ink" | "primary";
  /** Up to 4 — rendered as translucent paper tiles */
  metrics?: Array<{ label: string; value: string }>;
  /** light / lightGhost Buttons */
  actions?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}
export declare function HeroPanel(props: HeroPanelProps): JSX.Element;

/** Translucent metric tile used inside HeroPanel. */
export interface MetricProps {
  label: string;
  value: string;
}
export declare function Metric(props: MetricProps): JSX.Element;
