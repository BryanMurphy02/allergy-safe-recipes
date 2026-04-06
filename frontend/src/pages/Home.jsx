/*
 * Home.jsx
 *
 * The main recipe browsing page. Owns all filter state and
 * coordinates the FilterPanel, recipe grid, and Pagination.
 *
 * On mount it fetches allergens, dietary tags, and cuisines
 * to populate the filter panel. Recipes are fetched whenever
 * the filters or page number change.
 */

import { useEffect, useState } from "react";
import {
  getAllergens,
  getCuisines,
  getDietaryTags,
  getRecipes,
} from "../api/client";
import FilterPanel from "../components/FilterPanel";
import Pagination from "../components/Pagination";
import RecipeCard from "../components/RecipeCard";

const DEFAULT_FILTERS = {
  excludeAllergens: [],
  dietaryTags: [],
  cuisine: null,
  maxTotalTime: null,
};

const PAGE_SIZE = 20;

export default function Home() {
  // Reference data for the filter panel
  const [allergens, setAllergens]   = useState([]);
  const [dietaryTags, setDietaryTags] = useState([]);
  const [cuisines, setCuisines]     = useState([]);

  // Filter state
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [page, setPage]       = useState(1);

  // Recipe results
  const [recipes, setRecipes]   = useState([]);
  const [total, setTotal]       = useState(0);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  // Fetch reference data once on mount
  useEffect(() => {
    Promise.all([getAllergens(), getDietaryTags(), getCuisines()])
      .then(([a, t, c]) => {
        setAllergens(a);
        setDietaryTags(t);
        setCuisines(c);
      })
      .catch(console.error);
  }, []);

  // Fetch recipes whenever filters or page changes
  useEffect(() => {
    setLoading(true);
    setError(null);

    getRecipes({
      page,
      size: PAGE_SIZE,
      cuisine:          filters.cuisine,
      excludeAllergens: filters.excludeAllergens,
      dietaryTags:      filters.dietaryTags,
      maxTotalTime:     filters.maxTotalTime,
    })
      .then((data) => {
        setRecipes(data.results);
        setTotal(data.total);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filters, page]);

  function handleFilterChange(newFilters) {
    setFilters(newFilters);
    setPage(1); // reset to page 1 whenever filters change
  }

  function handleReset() {
    setFilters(DEFAULT_FILTERS);
    setPage(1);
  }

  return (
    <main className="max-w-6xl mx-auto px-4 py-8">

      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Recipes</h1>
        <p className="text-gray-500 mt-1 text-sm">
          {total > 0
            ? `${total} recipes found`
            : loading
            ? "Loading..."
            : "No recipes found"}
        </p>
      </div>

      <div className="flex gap-8 items-start">

        {/* Filter sidebar */}
        <FilterPanel
          allergens={allergens}
          dietaryTags={dietaryTags}
          cuisines={cuisines}
          filters={filters}
          onChange={handleFilterChange}
          onReset={handleReset}
        />

        {/* Recipe grid */}
        <div className="flex-1 min-w-0">

          {/* Error state */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm mb-6">
              Could not load recipes. Please try again.
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="bg-white rounded-xl border border-gray-200 overflow-hidden animate-pulse"
                >
                  <div className="h-48 bg-gray-200" />
                  <div className="p-4 flex flex-col gap-3">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-100 rounded w-1/2" />
                    <div className="flex gap-2">
                      <div className="h-5 bg-gray-100 rounded-full w-16" />
                      <div className="h-5 bg-gray-100 rounded-full w-16" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && recipes.length === 0 && (
            <div className="text-center py-24">
              <p className="text-gray-400 text-lg mb-2">No recipes found</p>
              <p className="text-gray-400 text-sm mb-6">
                Try adjusting your filters
              </p>
              <button
                onClick={handleReset}
                className="text-brand-600 hover:text-brand-700 font-medium text-sm"
              >
                Clear all filters
              </button>
            </div>
          )}

          {/* Results */}
          {!loading && !error && recipes.length > 0 && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recipes.map((recipe) => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>

              <Pagination
                page={page}
                size={PAGE_SIZE}
                total={total}
                onPageChange={setPage}
              />
            </>
          )}

        </div>
      </div>
    </main>
  );
}