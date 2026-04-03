/*
 * AllergenBadge.jsx
 *
 * A small coloured pill that displays a single allergen name.
 * Used on recipe cards and the recipe detail page.
 *
 * Always renders in red/amber tones to signal a warning —
 * allergens should stand out visually.
 */

export default function AllergenBadge({ name, displayName }) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700 border border-red-200">
      <span className="w-1.5 h-1.5 rounded-full bg-red-500 flex-shrink-0" />
      {displayName ?? name}
    </span>
  );
}