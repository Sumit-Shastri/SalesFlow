import './Navbar.css'
/*
#############################################################

# Methods

#############################################################

#############################################################

# Method Name : Navbar()

# Description : This method creates and displays the navigation

# bar for the SalesFlow application. It displays

# the SalesFlow logo, navigation links such as

# Home, Features, and Dashboard, and a Get Started

# button to navigate to different sections of

# the application.

# Parameters  : None

# Returns     : JSX.Element

# Author      : vishwajeet Dupargude

# Date        : 08-10-2026

#############################################################
*/
function Navbar() {
return ( <nav className="navbar"> <a href="#home" className="logo"> <span className="logo-icon">S</span>
SalesFlow </a>

```
  <div className="nav-links">
    <a href="#home">Home</a>
    <a href="#features">Features</a>
    <a href="#dashboard">Dashboard</a>
  </div>

  <a href="#features" className="nav-button">
    Get Started <span>→</span>
  </a>
</nav>


)
}

export default Navbar
