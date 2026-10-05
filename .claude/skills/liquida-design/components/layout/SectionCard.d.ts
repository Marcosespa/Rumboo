/**
 * 28px-radius paper section card with header and optional action.
 */
export interface SectionCardProps {
  title?: string;
  /** One sentence explaining what the section answers */
  subtitle?: string;
  /** Right-aligned header action (text link button) */
  action?: React.ReactNode;
  children?: React.ReactNode;
  className?: string;
}
export declare function SectionCard(props: SectionCardProps): JSX.Element;
