import { Link, NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2">
          <span className="text-brand-600 text-2xl font-bold tracking-tight">
            Safe<span className="text-gray-900">Plate</span>
          </span>
        </Link>

        {/* Navigation links */}
        <div className="flex items-center gap-6">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `text-sm font-medium transition-colors ${
                isActive
                  ? "text-brand-600"
                  : "text-gray-500 hover:text-gray-900"
              }`
            }
          >
            Recipes
          </NavLink>
          <NavLink
            to="/about"
            className={({ isActive }) =>
              `text-sm font-medium transition-colors ${
                isActive
                  ? "text-brand-600"
                  : "text-gray-500 hover:text-gray-900"
              }`
            }
          >
            About
          </NavLink>
        </div>

      </div>
    </nav>
  );
}