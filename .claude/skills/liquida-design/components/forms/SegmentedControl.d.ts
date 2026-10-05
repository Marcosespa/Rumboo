/**
 * Segmented toggle on a cloudSoft track; the active segment is ink with paper text.
 */
export interface SegmentedControlProps {
  /** Strings or { value, label } pairs */
  options: Array<string | { value: string; label: string }>;
  value?: string;
  onChange?: (value: string) => void;
  /** Stretch segments to fill the row. @default false */
  block?: boolean;
  className?: string;
}
export declare function SegmentedControl(props: SegmentedControlProps): JSX.Element;
