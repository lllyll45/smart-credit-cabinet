type LoaderProps = {
  text?: string
}

export default function Loader({
  text = 'Загрузка...',
}: LoaderProps) {
  return (
    <div className="loader-container" role="status">
      <span className="loader" />
      <span>{text}</span>
    </div>
  )
}