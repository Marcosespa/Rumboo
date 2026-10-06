/**
 * Lucide icon rendered from the Lucide UMD registry (window.lucide).
 */
export interface IconProps {
  /** Lucide icon name in PascalCase, e.g. "Camera", "CarFront", "TriangleAlert" */
  name: string;
  /** Square size in px. UI default is 16. @default 16 */
  size?: number;
  /** @default 2 */
  strokeWidth?: number;
  /** @default "currentColor" */
  color?: string;
  style?: React.CSSProperties;
}
export declare function Icon(props: IconProps): JSX.Element;
