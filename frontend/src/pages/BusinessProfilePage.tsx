import { useEffect, useState, type FormEvent } from 'react'
import PageLayout from '../components/layout/PageLayout'
import Loader from '../components/ui/Loader'
import Input from '../components/ui/Input'
import Button from '../components/ui/Button'
import {
  fetchBusinessProfile,
  upsertBusinessProfile,
} from '../features/businessProfile/profileApi'
import { getErrorMessage } from '../utils/getErrorMessage'
import type { BusinessProfile } from '../types/comon'

const emptyForm = {
  business_name: '',
  legal_form: 'OOO',
  industry: '',
  region: '',
  business_start_date: '',
  monthly_revenue: '',
}

export default function BusinessProfilePage() {
  const [profile, setProfile] = useState<BusinessProfile | null>(null)
  const [form, setForm] = useState(emptyForm)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    let active = true
    async function load() {
      try {
        const data = await fetchBusinessProfile()
        if (!active) return
        setProfile(data)
        if (data) {
          setForm({
            business_name: data.business_name,
            legal_form: data.legal_form,
            industry: data.industry,
            region: data.region,
            business_start_date: data.business_start_date,
            monthly_revenue: String(data.monthly_revenue),
          })
        }
      } catch (err) {
        if (active) setError(getErrorMessage(err))
      } finally {
        if (active) setLoading(false)
      }
    }
    void load()
    return () => {
      active = false
    }
  }, [])

  function update<K extends keyof typeof form>(
    key: K,
    value: string,
  ) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (!form.business_name.trim()) {
      setError('Укажите название бизнеса.')
      return
    }
    if (!form.business_start_date) {
      setError('Укажите дату начала деятельности.')
      return
    }
    const revenue = Number(form.monthly_revenue)
    if (!Number.isFinite(revenue) || revenue < 0) {
      setError('Укажите корректный ежемесячный доход.')
      return
    }

    setSaving(true)
    try {
      const data = await upsertBusinessProfile({
        business_name: form.business_name.trim(),
        legal_form: form.legal_form.trim() || 'OOO',
        industry: form.industry.trim(),
        region: form.region.trim(),
        business_start_date: form.business_start_date,
        monthly_revenue: revenue,
      })
      setProfile(data)
      setSuccess('Профиль бизнеса сохранён.')
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setSaving(false)
    }
  }

  return (
    <PageLayout>
      <div className="page-heading">
        <span className="eyebrow">Профиль</span>
        <h1>Профиль бизнеса</h1>
        <p>
          Заполните данные, чтобы получать более точные рекомендации
          кредитных продуктов.
        </p>
      </div>

      {loading && <Loader text="Загружаем профиль..." />}

      {!loading && (
        <form className="content-card" onSubmit={handleSubmit}>
          <div className="form-grid">
            <Input
              label="Название бизнеса"
              value={form.business_name}
              onChange={(e) => update('business_name', e.target.value)}
              required
            />
            <Input
              label="Правовая форма (ООО, ИП и т.д.)"
              value={form.legal_form}
              onChange={(e) => update('legal_form', e.target.value)}
              required
            />
            <Input
              label="Отрасль"
              value={form.industry}
              onChange={(e) => update('industry', e.target.value)}
              required
            />
            <Input
              label="Регион"
              value={form.region}
              onChange={(e) => update('region', e.target.value)}
              required
            />
            <Input
              label="Дата начала деятельности"
              type="date"
              value={form.business_start_date}
              onChange={(e) =>
                update('business_start_date', e.target.value)
              }
              required
            />
            <Input
              label="Ежемесячная выручка, ₽"
              type="number"
              min="0"
              value={form.monthly_revenue}
              onChange={(e) =>
                update('monthly_revenue', e.target.value)
              }
              required
            />
          </div>

          {error && <p className="form-error">{error}</p>}
          {success && <p className="form-success">{success}</p>}

          <Button type="submit" loading={saving} className="button-spaced">
            {profile ? 'Сохранить изменения' : 'Создать профиль'}
          </Button>
        </form>
      )}
    </PageLayout>
  )
}