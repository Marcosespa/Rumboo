/** 44×44 bordered square icon button used in the app header. */
export interface IconButtonProps {
  /** Lucide icon name, e.g. "RefreshCw", "LogOut" */
  icon: string;
  /** Accessible label (required — icon-only control) */
  label: string;
  /** Icon size in px. @default 16 */
  size?: number;
  onClick?: () => void;
  className?: string;
}
export declare function IconButton(props: IconButtonProps): JSX.Element;
