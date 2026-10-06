/**
 * Sticky page header with brand chip, 28px title and utility actions.
 */
export interface AppHeaderProps {
  /** Page title, e.g. "Hola, Marcos" or "Alertas" */
  title: string;
  /** One-sentence orientation copy */
  subtitle?: string;
  /** Path to condor-sm.png (logo always accompanies the wordmark) */
  logoSrc?: string;
  /** Extra chip/badge before the icon buttons */
  rightMeta?: React.ReactNode;
  /** Shows the RefreshCw icon button */
  onRefresh?: () => void;
  /** Shows the LogOut icon button */
  onLogout?: () => void;
  className?: string;
}
export declare function AppHeader(props: AppHeaderProps): JSX.Element;

/** Pill with the condor mark + "Rumbo" wordmark. */
export interface BrandChipProps {
  logoSrc?: string;
  children?: React.ReactNode;
  className?: string;
}
export declare function BrandChip(props: BrandChipProps): JSX.Element;
