/** Round filter chip; active = ink fill with paper text. */
export interface FilterChipProps {
  /** @default false */
  active?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
  className?: string;
}
export declare function FilterChip(props: FilterChipProps): JSX.Element;
