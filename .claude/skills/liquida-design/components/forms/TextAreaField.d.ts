/** Labeled textarea with the Field skin. */
export interface TextAreaFieldProps {
  label?: string;
  /** @default 3 */
  rows?: number;
  placeholder?: string;
  value?: string;
  /** Receives the new VALUE (not the event) */
  onChange?: (value: string) => void;
  className?: string;
}
export declare function TextAreaField(props: TextAreaFieldProps): JSX.Element;
