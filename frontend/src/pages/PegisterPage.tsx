import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import Loader from '../components/ui/Loader'
import { useAuth } from '../hooks/useAuth'
import axios from 'axios'

export default function RegisterPage() {
  const { register, user, loading } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return <Loader />
  if (user) return <Navigate to="/dashboard" replace />

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')

    if (password.length < 8) {
      setError('Пароль должен содержать не менее 8 символов.')
      return
    }

    if (password !== confirmPassword) {
      setError('Пароли не совпадают.')
      return
    }

    setSubmitting(true)
    try {
      await register(email, password)
      navigate('/dashboard', { replace: true })
    } catch (err: unknown) {
      if (axios.isAxiosError(err)) {
        const status = err.response?.status
        const detail = err.response?.data?.detail

        if (status === 422) {
          setError('Введите корректный email и проверьте заполнение полей.')
        } else if (status === 409) {
          setError('Пользователь с таким email уже существует.')
        } else if (!err.response) {
          setError('Не удалось связаться с сервером. Попробуйте позже.')
        } else if (typeof detail === 'string') {
          setError(detail)
        } else {
          setError('Не удалось зарегистрироваться. Попробуйте позже.')
        }
      } else {
        setError('Произошла непредвиденная ошибка. Попробуйте позже.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="page-content">
      <section className="auth-card">
        <Link to="/login" className="brand">
          <span className="brand-icon">₽</span>
          <span>Smart Credit</span>
        </Link>

        <div className="page-heading">
          <span className="eyebrow">Новый пользователь</span>
          <h1>Создание аккаунта</h1>
          <p>Зарегистрируйтесь для работы с кредитными продуктами.</p>
        </div>

        <form onSubmit={handleSubmit}>
          <Input
            label="Email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
          <Input
            label="Пароль"
            name="password"
            type="password"
            autoComplete="new-password"
            minLength={8}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          <Input
            label="Повторите пароль"
            name="confirmPassword"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            required
          />

          {error && <p className="form-error">{error}</p>}

          <Button type="submit" disabled={submitting}>
            {submitting ? 'Создаём аккаунт...' : 'Зарегистрироваться'}
          </Button>
        </form>

        <p className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </section>
    </main>
  )
}