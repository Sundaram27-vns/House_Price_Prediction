import { useState } from 'react'

const initial = {
  overall_qual: 7,
  living_area: 1900,
  garage_cars: 2,
  basement_area: 1050,
  full_baths: 2,
  year_built: 2005,
  neighborhood: 'CollgCr',
  kitchen_quality: 'Gd',
}

const neighborhoods = [
  ['Blmngtn', 'Bloomington Heights'],
  ['Blueste', 'Bluestem'],
  ['BrDale', 'Briardale'],
  ['BrkSide', 'Brookside'],
  ['ClearCr', 'Clear Creek'],
  ['CollgCr', 'College Creek'],
  ['Crawfor', 'Crawford'],
  ['Edwards', 'Edwards'],
  ['Gilbert', 'Gilbert'],
  ['IDOTRR', 'Iowa DOT and Rail Road'],
  ['MeadowV', 'Meadow Village'],
  ['Mitchel', 'Mitchell'],
  ['NAmes', 'North Ames'],
  ['NoRidge', 'Northridge'],
  ['NPkVill', 'Northpark Villa'],
  ['NridgHt', 'Northridge Heights'],
  ['NWAmes', 'Northwest Ames'],
  ['OldTown', 'Old Town'],
  ['SWISU', 'South & West of Iowa State'],
  ['Sawyer', 'Sawyer'],
  ['SawyerW', 'Sawyer West'],
  ['Somerst', 'Somerset'],
  ['StoneBr', 'Stone Brook'],
  ['Timber', 'Timberland'],
  ['Veenker', 'Veenker'],
]

const money = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

export default function App() {
  const [form, setForm] = useState(initial)
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  function update(event) {
    const { name, value } = event.target
    setForm((current) => ({
      ...current,
      [name]: name === 'neighborhood' || name === 'kitchen_quality' ? value : Number(value),
    }))
  }

  async function submit(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || 'Could not estimate this home.')
      setResult(payload.estimated_price)
    } catch (err) {
      setError(err.message.includes('fetch') ? 'The server is not running. Start the backend and try again.' : err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="top">
        <div className="wrap top-inner">
          <a className="logo" href="#top">
            <span className="logo-icon" aria-hidden="true">⌂</span>
            House of Hearth
          </a>
          <nav className="nav-links"><a className="nav-current" href="#top">Overview</a><a href="#estimate">Home estimate</a><a href="#about">About</a></nav>
          <div className="nav-actions"><span className="place">⌖ &nbsp; Ames, Iowa</span><a className="nav-cta" href="#estimate">Get started</a></div>
        </div>
      </header>

      <main className="wrap">
        <section className="intro" id="top">
          <div className="intro-copy"><span className="eyebrow">A SMARTER WAY TO FIND YOUR HOME’S VALUE</span>
          <h1>A clearer view of<br />your home’s <em>value.</em></h1>
          <p>Get a thoughtful estimate based on your property details and real historical home sales in Ames, Iowa.</p></div>
          <a className="prompt-bar" href="#estimate"><span className="prompt-icon">⌂</span><span>Discover what your home could be worth</span><b>Start estimating <i>→</i></b></a>
          <div className="quick-links"><a href="#estimate">✦ &nbsp;Quick and simple</a><a href="#about">↗ &nbsp;Based on local sales</a><a href="#estimate">⌖ &nbsp;Ames, Iowa</a></div>
        </section>

        <div className="layout" id="estimate">
          <form className="card" onSubmit={submit}>
            <h2>House details</h2>

            <div className="fields">
              <label>
                Living area (sq ft)
                <input type="number" name="living_area" min="200" max="10000" value={form.living_area} onChange={update} required />
              </label>
              <label>
                Basement area (sq ft)
                <input type="number" name="basement_area" min="0" max="6000" value={form.basement_area} onChange={update} required />
              </label>
              <label>
                Full bathrooms
                <input type="number" name="full_baths" min="0" max="5" value={form.full_baths} onChange={update} required />
              </label>
              <label>
                Garage (cars)
                <input type="number" name="garage_cars" min="0" max="5" value={form.garage_cars} onChange={update} required />
              </label>
              <label>
                Overall quality
                <select name="overall_qual" value={form.overall_qual} onChange={update}>
                  {Array.from({ length: 10 }, (_, i) => (
                    <option key={i + 1} value={i + 1}>
                      {i + 1} — {['Very poor', 'Poor', 'Fair', 'Below average', 'Average', 'Above average', 'Good', 'Very good', 'Excellent', 'Very excellent'][i]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Year built
                <input type="number" name="year_built" min="1870" max="2010" value={form.year_built} onChange={update} required />
              </label>
              <label>
                Neighborhood
                <select name="neighborhood" value={form.neighborhood} onChange={update}>
                  {neighborhoods.map(([id, label]) => (
                    <option key={id} value={id}>{label}</option>
                  ))}
                </select>
              </label>
              <label>
                Kitchen quality
                <select name="kitchen_quality" value={form.kitchen_quality} onChange={update}>
                  <option value="Ex">Excellent</option>
                  <option value="Gd">Good</option>
                  <option value="TA">Average</option>
                  <option value="Fa">Fair</option>
                  <option value="Po">Poor</option>
                </select>
              </label>
            </div>

            {error ? <p className="error" role="alert">{error}</p> : null}

            <button type="submit" disabled={busy}>
              {busy ? 'Calculating…' : 'Get price'}
            </button>
          </form>

          <aside className="card result">
            <h2>Estimated price</h2>
            {result == null ? (
              <p className="hint">Enter the house details and click Get price. The estimate will show up here.</p>
            ) : (
              <>
                <p className="price">{money.format(result)}</p>
                <p className="hint">This is a practice estimate from past Ames sales. It is not a real appraisal.</p>
              </>
            )}
          </aside>
        </div>
      </main>

      <footer className="foot" id="about">
        <div className="wrap">Data from Ames, Iowa home sales (2006–2010). For learning only.</div>
      </footer>
    </div>
  )
}
