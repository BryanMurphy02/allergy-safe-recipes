/*
 * RecipeCard.jsx
 *
 * Displays a single recipe in the grid on the home page.
 * Shows the image, title, cuisine, prep time, servings,
 * allergen badges, and dietary tag badges.
 *
 * Clicking the card navigates to the recipe detail page.
 */

import { useNavigate } from "react-router-dom";
import AllergenBadge from "./AllergenBadge";
import DietaryBadge from "./DietaryBadge";

export default function RecipeCard({ recipe }) {
  const navigate = useNavigate();

  const {
    id,
    title,
    image_url,
    cuisine,
    prep_time,
    cook_time,
    total_time,
    servings,
    allergens,
    dietary_tags,
  } = recipe;

  const timeLabel = total_time
    ? `${total_time} min`
    : prep_time
    ? `${prep_time} min prep`
    : cook_time
    ? `${cook_time} min cook`
    : null;

  const hasAllergens = allergens?.length > 0;

  return (
    <div
      onClick={() => navigate(`/recipes/${id}`)}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md hover:border-gray-300 transition-all duration-200 flex flex-col"
    >
      {/* Image */}
      <div className="relative h-48 bg-gray-100 overflow-hidden">
        {image_url ? (
          <img
            src={image_url}
            alt={title}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-300 text-4xl">
            🍽
          </div>
        )}

        {/* Allergen warning overlay */}
        {hasAllergens && (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs font-semibold px-2 py-1 rounded-full">
            Contains allergens
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col gap-3 flex-1">

        {/* Title */}
        <h3 className="font-semibold text-gray-900 leading-snug line-clamp-2">
          {title}
        </h3>

        {/* Meta — cuisine, time, servings */}
        <div className="flex items-center gap-3 text-xs text-gray-500">
          {cuisine && (
            <span className="bg-gray-100 px-2 py-0.5 rounded-full">
              {cuisine}
            </span>
          )}
          {timeLabel && <span>⏱ {timeLabel}</span>}
          {servings && <span>👤 Serves {servings}</span>}
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-1.5 mt-auto">
          {allergens?.map((a) => (
            <AllergenBadge key={a.id} name={a.name} displayName={a.display_name} />
          ))}
          {dietary_tags?.map((t) => (
            <DietaryBadge key={t.id} name={t.name} displayName={t.display_name} />
          ))}
        </div>

      </div>
    </div>
  );
}