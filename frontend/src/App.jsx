import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Home from "./Page/Home";
import Dashboard from "./Page/Dashboard";
import Loader from "./Page/Loader";
import Cleaner from "./Page/Cleaner";
import Validator from "./Page/Validator";
import Analyzer from "./Page/analyzer";

function App() {
return ( <BrowserRouter> <Routes>
<Route path="/" element={<Home />} />
<Route path="/dashboard" element={<Dashboard />} />
<Route path="/loader" element={<Loader />} />
<Route path="/cleaner" element={<Cleaner />} />
<Route path="/validator" element={<Validator />} />
<Route path="/analyzer" element={<Analyzer />} />
<Route path="*" element={<Navigate to="/" replace />} /> </Routes> </BrowserRouter>
);
}

export default App;
