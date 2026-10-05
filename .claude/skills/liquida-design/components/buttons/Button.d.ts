/**
 * Rumbo button — rounded-16px, 44px min height, lift-on-hover.
 */
export interface ButtonProps {
  /**
   * primary = azul ruta (default action) · accent = ámbar señal (ONLY for the
   * main "Tomar foto" CTA) · secondary = bordered paper · light / lightGhost =
   * for use on dark ink/primary panels · ghost = tertiary.
   * @default "primary"
   */
  variant?: "primary" | "accent" | "secondary" | "light" | "lightGhost" | "ghost";
  /** "lg" = 56px-tall road-friendly CTA */
  size?: "lg";
  /** Full width. @default false */
  block?: boolean;
  /** Shows spinner + "Espera..." and disables. @default false */
  loading?: boolean;
  /** Render element/tag. @default "button" */
  as?: string;
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
  children?: React.ReactNode;
}
export declare function Button(props: ButtonProps): JSX.Element;
