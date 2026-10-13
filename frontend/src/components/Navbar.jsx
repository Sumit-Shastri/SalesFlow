import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
const [servicesOpen, setServicesOpen] = useState(false);
const location = useLocation();

const services = [
{ name: "Data Loader", path: "/loader" },
{ name: "Data Cleaner", path: "/cleaner" },
{ name: "Data Validator", path: "/validator" },
{ name: "Data Analyzer", path: "/analyzer" },
];

return ( <nav className="navbar"> <Link to="/" className="navbar-brand"> <div className="navbar-logo">S</div> <span>SalesFlow</span> </Link>


  <div className="navbar-links">
    <Link
      to="/"
      className={`nav-link ${location.pathname === "/" ? "active" : ""}`}
    >
      Home
    </Link>

    <Link
      to="/dashboard"
      className={`nav-link ${
        location.pathname === "/dashboard" ? "active" : ""
      }`}
    >
      Dashboard
    </Link>

    <div className="services-menu">
      <button
        type="button"
        className={`nav-link services-button ${
          services.some((service) => service.path === location.pathname)
            ? "active"
            : ""
        }`}
        onClick={() => setServicesOpen((open) => !open)}
        aria-expanded={servicesOpen}
      >
        Services <span className="dropdown-arrow">⌄</span>
      </button>

      {servicesOpen && (
        <div className="dropdown-menu">
          {services.map((service) => (
            <Link
              key={service.path}
              to={service.path}
              className="dropdown-item"
              onClick={() => setServicesOpen(false)}
            >
              {service.name}
            </Link>
          ))}
        </div>
      )}
    </div>
  </div>
</nav>


);
}

export default Navbar;
