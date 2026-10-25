import type { SelectHTMLAttributes } from 'react'

type SelectOption = {
  label: string
  value: string
}

type SelectProps = SelectHTMLAttributes<HTMLSelectElement> & {
  label: string
  options: SelectOption[]
  error?: string
}

export default function Select({
  label,
  options,
  error,
  id,
  ...props
}: SelectProps) {
  const selectId = id ?? props.name

  return (
    <div className="form-field">
      <label htmlFor={selectId}>{label}</label>

      <select
        {...props}
        id={selectId}
        className={`input ${error ? 'input--error' : ''}`}
      >
        <option value="">Выберите вариант</option>

        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {error && <p className="field-error">{error}</p>}
    </div>
  )
}