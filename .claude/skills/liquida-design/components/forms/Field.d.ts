/** Labeled text input (cloudSoft fill, primary focus ring). */
export interface FieldProps {
  label?: string;
  /** Small mist helper text under the input */
  hint?: string;
  placeholder?: string;
  /** @default "text" */
  type?: string;
  value?: string;
  /** Receives the new VALUE (not the event) */
  onChange?: (value: string) => void;
  className?: string;
}
export declare function Field(props: FieldProps): JSX.Element;
