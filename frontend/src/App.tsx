import { useState, useEffect } from 'react'
import './App.css'
import { ApiStatus } from '@/components/ApiStatus'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="app">
      <header className="app-header">
        <h1>{{ cookiecutter.project_name }}</h1>
        <p>{{ cookiecutter.project_short_description }}</p>
      </header>

      <main className="app-main">
        <section className="demo-section">
          <h2>React + TypeScript + Vite</h2>
          <div className="card">
            <button onClick={() => setCount((count) => count + 1)}>
              Count is {count}
            </button>
            <p>
              Edit <code>src/App.tsx</code> and save to test HMR
            </p>
          </div>
        </section>

        <section className="api-section">
          <h2>Backend API Status</h2>
          <ApiStatus />
        </section>
      </main>

      <footer className="app-footer">
        <p>
          Built with{' '}
          <a href="https://vite.dev" target="_blank" rel="noopener noreferrer">
            Vite
          </a>
          {' + '}
          <a href="https://react.dev" target="_blank" rel="noopener noreferrer">
            React
          </a>
          {' + '}
          <a href="https://fastapi.tiangolo.com" target="_blank" rel="noopener noreferrer">
            FastAPI
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
