/**
 * Alert card for vencimientos, cartera y servicios.
 */
export interface AlertCardProps {
  /** attention = cloudSoft · critical = error-tinted. @default "attention" */
  severity?: "attention" | "critical";
  title: string;
  detail?: string;
  /** Uppercase meta line: kind · date · amount */
  meta?: string;
  /** Show the severity pill. @default true */
  pill?: boolean;
  /** Action buttons rendered in a responsive grid */
  actions?: React.ReactNode;
  className?: string;
}
export declare function AlertCard(props: AlertCardProps): JSX.Element;
