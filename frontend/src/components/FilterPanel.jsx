/*
 * FilterPanel.jsx
 *
 * The left sidebar filter UI on the home page.
 * Lets users filter recipes by:
 *   - Allergens to exclude
 *   - Dietary tags to require
 *   - Cuisine
 *   - Max total cook time
 *
 * All filter state lives in the parent (Home.jsx) and is
 * passed down as props. This component only renders the UI
 * and calls the onChange callbacks when the user interacts.
 */

export default function FilterPanel({
  allergens,
  dietaryTags,
  cuisines,
  filters,
  onChange,
  onReset,
}) {
  function toggleAllergen(name) {
    const current = filters.excludeAllergens ?? [];
    const updated = current.includes(name)
      ? current.filter((a) => a !== name)
      : [...current, name];
    onChange({ ...filters, excludeAllergens: updated });
  }

  function toggleDietaryTag(name) {
    const current = filters.dietaryTags ?? [];
    const updated = current.includes(name)
      ? current.filter((t) => t !== name)
      : [...current, name];
    onChange({ ...filters, dietaryTags: updated });
  }

  const activeFilterCount =
    (filters.excludeAllergens?.length ?? 0) +
    (filters.dietaryTags?.length ?? 0) +
    (filters.cuisine ? 1 : 0) +
    (filters.maxTotalTime ? 1 : 0);

  return (
    <aside className="w-64 flex-shrink-0">
      <div className="bg-white rounded-xl border border-gray-200 p-5 sticky top-24 flex flex-col gap-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">Filters</h2>
          {activeFilterCount > 0 && (
            <button
              onClick={onReset}
              className="text-xs text-brand-600 hover:text-brand-700 font-medium"
            >
              Reset ({activeFilterCount})
            </button>
          )}
        </div>

        {/* Exclude allergens */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Exclude allergens
          </h3>
          <div className="flex flex-col gap-2">
            {allergens.map((a) => (
              <label key={a.id} className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={filters.excludeAllergens?.includes(a.name) ?? false}
                  onChange={() => toggleAllergen(a.name)}
                  className="w-4 h-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                />
                <span className="text-sm text-gray-700 group-hover:text-gray-900">
                  {a.display_name}
                </span>
              </label>
            ))}
          </div>
        </section>

        {/* Dietary preferences */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Dietary preferences
          </h3>
          <div className="flex flex-col gap-2">
            {dietaryTags.map((t) => (
              <label key={t.id} className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={filters.dietaryTags?.includes(t.name) ?? false}
                  onChange={() => toggleDietaryTag(t.name)}
                  className="w-4 h-4 rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                />
                <span className="text-sm text-gray-700 group-hover:text-gray-900">
                  {t.display_name}
                </span>
              </label>
            ))}
          </div>
        </section>

        {/* Cuisine */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Cuisine
          </h3>
          <select
            value={filters.cuisine ?? ""}
            onChange={(e) =>
              onChange({ ...filters, cuisine: e.target.value || null })
            }
            className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 text-gray-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="">All cuisines</option>
            {cuisines.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </section>

        {/* Max total time */}
        <section>
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Max cook time
          </h3>
          <div className="flex flex-col gap-2">
            {[15, 30, 60, 90].map((mins) => (
              <label key={mins} className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="radio"
                  name="maxTotalTime"
                  checked={filters.maxTotalTime === mins}
                  onChange={() => onChange({ ...filters, maxTotalTime: mins })}
                  className="w-4 h-4 border-gray-300 text-brand-600 focus:ring-brand-500"
                />
                <span className="text-sm text-gray-700 group-hover:text-gray-900">
                  Under {mins} min
                </span>
              </label>
            ))}
            {filters.maxTotalTime && (
              <button
                onClick={() => onChange({ ...filters, maxTotalTime: null })}
                className="text-xs text-gray-400 hover:text-gray-600 text-left mt-1"
              >
                Clear time filter
              </button>
            )}
          </div>
        </section>

      </div>
    </aside>
  );
}