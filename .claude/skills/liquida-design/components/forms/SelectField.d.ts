/** Labeled select with the same skin as Field. */
export interface SelectFieldProps {
  label?: string;
  /** Strings or { value, label } pairs */
  options: Array<string | { value: string; label: string }>;
  value?: string;
  /** Receives the new VALUE (not the event) */
  onChange?: (value: string) => void;
  className?: string;
}
export declare function SelectField(props: SelectFieldProps): JSX.Element;
