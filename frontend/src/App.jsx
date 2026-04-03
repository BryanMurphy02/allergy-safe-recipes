/*
 * App.jsx
 *
 * Root component. Defines the route structure and wraps
 * every page in the shared Navbar layout.
 */

import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import RecipeDetail from "./pages/RecipeDetail";
import About from "./pages/About";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <Routes>
        <Route path="/"            element={<Home />} />
        <Route path="/recipes/:id" element={<RecipeDetail />} />
        <Route path="/about"       element={<About />} />
        <Route path="*"            element={<NotFound />} />
      </Routes>
    </div>
  );
}

function NotFound() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-24 text-center">
      <h1 className="text-3xl font-bold text-gray-900 mb-3">404</h1>
      <p className="text-gray-500 mb-6">This page does not exist.</p>
      <a
        href="/"
        className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-medium px-6 py-3 rounded-xl transition-colors"
      >
        Go home
      </a>
    </main>
  );
}