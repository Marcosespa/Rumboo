/** Movement row: title/meta left, signed COP amount right. */
export interface ListRowProps {
  /** Merchant or category, e.g. "Estación Terpel La 80" */
  title: string;
  /** "Categoría · fecha" meta line */
  meta?: string;
  /** Pre-formatted COP amount, e.g. "$ 180.000" */
  amount: string;
  /** expense = error red with minus · income = primary blue. @default "neutral" */
  tone?: "expense" | "income" | "neutral";
  className?: string;
}
export declare function ListRow(props: ListRowProps): JSX.Element;
