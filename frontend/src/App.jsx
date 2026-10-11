import Navbar from './components/Navbar'
import './App.css'

function App() {
  return (
    <>
      <Navbar />

      <main className="hero" id="features">

        {/* Background Decorations */}
        <div className="hero-circle hero-circle-top"></div>
        <div className="hero-circle hero-circle-bottom"></div>

        <div className="hero-content">

          {/* Badge */}
          <div className="hero-badge">
            <span className="trend-icon">↗</span>
            <span>Smarter Sales. Better Decisions.</span>
          </div>

          {/* Heading */}
          <h1 className="hero-title">
            Welcome to
            <br />
            <span>SalesFlow</span>
          </h1>

          {/* Description */}
          <p className="hero-description">
            Turn your sales data into clear insights.
            <br />
            Track, analyze and grow — all in one place.
          </p>


        </div>
      </main>
    </>
  )
}

export default App