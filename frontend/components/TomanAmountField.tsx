"use client";

import { formatGroupedTomanInput } from "@/shared/format";

export default function TomanAmountField({
  value,
  onChange,
  placeholder,
  ariaLabel,
  className = "input input-light",
  id,
}: {
  value: string;
  onChange: (next: string) => void;
  placeholder?: string;
  ariaLabel?: string;
  className?: string;
  id?: string;
}) {
  return (
    <input
      id={id}
      className={`${className} num toman-input`}
      inputMode="numeric"
      autoComplete="off"
      value={value}
      onChange={(event) => onChange(formatGroupedTomanInput(event.target.value))}
      placeholder={placeholder}
      aria-label={ariaLabel}
    />
  );
}
