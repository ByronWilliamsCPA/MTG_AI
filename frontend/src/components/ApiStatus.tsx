import { useState, useEffect } from 'react'
import { useApi } from '@/hooks/useApi'
import './ApiStatus.css'

interface HealthStatus {
  status: string
  timestamp?: string
  version?: string
}

export function ApiStatus() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const api = useApi()

  useEffect(() => {
    const checkHealth = async () => {
      try {
        setLoading(true)
        setError(null)
        const response = await api.get<HealthStatus>('/health/live')
        setHealth(response.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to connect to API')
        setHealth(null)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()

    // Poll health status every 30 seconds
    const interval = setInterval(checkHealth, 30000)
    return () => clearInterval(interval)
  }, [api])

  if (loading) {
    return (
      <div className="api-status api-status--loading">
        <span className="api-status__indicator"></span>
        <span>Checking API connection...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="api-status api-status--error">
        <span className="api-status__indicator"></span>
        <div>
          <strong>API Offline</strong>
          <p>{error}</p>
          <small>Make sure the backend is running on port 8000</small>
        </div>
      </div>
    )
  }

  return (
    <div className="api-status api-status--connected">
      <span className="api-status__indicator"></span>
      <div>
        <strong>API Connected</strong>
        <p>Status: {health?.status || 'healthy'}</p>
        {health?.version && <small>Version: {health.version}</small>}
      </div>
    </div>
  )
}
