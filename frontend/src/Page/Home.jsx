import Navbar from '../components/Navbar'
import "../style/Home.css";

function Home() {
  return (
    <>
      <Navbar />

      <main className="hero">
        <h1>Welcome to SalesFlow</h1>

        <p>Turn your sales data into clear insights.</p>

        <a href="/dashboard">
          Get Started
        </a>
      </main>
    </>
  )
}

export default Home