import { NavLink } from "react-router-dom";
import logo from "../assets/logo.svg";

const linkClass = ({ isActive }) =>
  `rounded-full px-3 py-1.5 text-sm font-medium ${
    isActive ? "bg-teal-800 text-white" : "text-slate-700 hover:bg-white"
  }`;

export default function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between gap-4 px-4 py-3">
        <NavLink to="/" className="flex items-center gap-2 font-semibold text-ink">
          <img src={logo} alt="" className="h-8 w-8" />
          <span>Phishing Detector</span>
        </NavLink>
        <nav className="flex items-center gap-1">
          <NavLink to="/" className={linkClass} end>
            Inicio
          </NavLink>
          <NavLink to="/about" className={linkClass}>
            Acerca de
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
