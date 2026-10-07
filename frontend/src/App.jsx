import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import About from "./pages/About.jsx";
import Home from "./pages/Home.jsx";
import NotFound from "./pages/NotFound.jsx";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <footer className="border-t border-slate-200 px-4 py-4 text-center text-xs text-slate-500">
        Proyecto educativo. No reemplaza un antivirus ni un filtro corporativo.
      </footer>
    </div>
  );
}
