/*
 * DietaryBadge.jsx
 *
 * A small coloured pill that displays a single dietary tag.
 * Used on recipe cards and the recipe detail page.
 *
 * Each tag has its own colour so they're visually distinct
 * from each other and from allergen badges.
 */

const TAG_STYLES = {
  vegetarian:       "bg-green-100 text-green-700 border-green-200",
  vegan:            "bg-emerald-100 text-emerald-700 border-emerald-200",
  gluten_free:      "bg-amber-100 text-amber-700 border-amber-200",
  contains_raw_egg: "bg-orange-100 text-orange-700 border-orange-200",
};

const DEFAULT_STYLE = "bg-gray-100 text-gray-700 border-gray-200";

export default function DietaryBadge({ name, displayName }) {
  const style = TAG_STYLES[name] ?? DEFAULT_STYLE;

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${style}`}
    >
      {displayName ?? name}
    </span>
  );
}