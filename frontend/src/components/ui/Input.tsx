import type { InputHTMLAttributes } from 'react'

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string
  error?: string
}

export default function Input({
  label,
  error,
  id,
  ...props
}: InputProps) {
  const inputId = id ?? props.name

  return (
    <div className="form-field">
      <label htmlFor={inputId}>{label}</label>

      <input
        {...props}
        id={inputId}
        className={`input ${error ? 'input--error' : ''}`}
      />

      {error && <p className="field-error">{error}</p>}
    </div>
  )
}