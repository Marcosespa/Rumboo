/** Dashed-border empty state with an icon box and guidance copy. */
export interface EmptyStateProps {
  /** Lucide icon name. @default "Camera" */
  icon?: string;
  /** Friendly next-step copy, e.g. "Sube una foto para empezar." */
  text: string;
  className?: string;
}
export declare function EmptyState(props: EmptyStateProps): JSX.Element;
