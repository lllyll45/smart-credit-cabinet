import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'danger'
  loading?: boolean
}

export default function Button({
  children,
  variant = 'primary',
  loading = false,
  disabled,
  className = '',
  type = 'button',
  ...props
}: ButtonProps) {
  const variantClass = {
    primary: 'primary-button',
    secondary: 'secondary-button',
    danger: 'danger-button',
  }[variant]

  return (
    <button
      {...props}
      type={type}
      disabled={disabled || loading}
      className={`${variantClass} ${className}`.trim()}
    >
      {loading ? 'Загрузка…' : children}
    </button>
  )
}