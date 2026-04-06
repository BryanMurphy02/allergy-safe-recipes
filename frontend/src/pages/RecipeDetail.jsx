/*
 * RecipeDetail.jsx
 *
 * Full detail view for a single recipe.
 * Fetches the recipe by id from the URL parameter.
 *
 * Shows:
 *   - Image, title, description
 *   - Meta: cuisine, prep time, cook time, servings
 *   - Allergen warnings
 *   - Dietary tag badges
 *   - Full ingredient list
 *   - Link back to original BBC Good Food page
 */

import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { getRecipeById } from "../api/client";
import AllergenBadge from "../components/AllergenBadge";
import DietaryBadge from "../components/DietaryBadge";

export default function RecipeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [recipe, setRecipe]   = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    getRecipeById(id)
      .then(setRecipe)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-12">
        <div className="flex items-center justify-center py-24 text-gray-400">
          Loading recipe...
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="max-w-3xl mx-auto px-4 py-12">
        <div className="text-center py-24">
          <p className="text-gray-500 mb-4">Could not load this recipe.</p>
          <button
            onClick={() => navigate(-1)}
            className="text-brand-600 hover:text-brand-700 font-medium text-sm"
          >
            ← Go back
          </button>
        </div>
      </main>
    );
  }

  const {
    title,
    description,
    image_url,
    cuisine,
    prep_time,
    cook_time,
    total_time,
    servings,
    allergens,
    dietary_tags,
    ingredients,
    url,
  } = recipe;

  return (
    <main className="max-w-3xl mx-auto px-4 py-10">

      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 mb-6 transition-colors"
      >
        ← Back to recipes
      </button>

      {/* Image */}
      {image_url && (
        <div className="rounded-2xl overflow-hidden h-72 mb-8 bg-gray-100">
          <img
            src={image_url}
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>
      )}

      {/* Title */}
      <h1 className="text-3xl font-bold text-gray-900 mb-3">{title}</h1>

      {/* Description */}
      {description && (
        <p className="text-gray-600 leading-relaxed mb-6">{description}</p>
      )}

      {/* Meta */}
      <div className="flex flex-wrap gap-3 mb-8">
        {cuisine && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-700">
            🌍 {cuisine}
          </div>
        )}
        {prep_time && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-700">
            ⏱ Prep {prep_time} min
          </div>
        )}
        {cook_time && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-700">
            🍳 Cook {cook_time} min
          </div>
        )}
        {total_time && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-700">
            ⏰ Total {total_time} min
          </div>
        )}
        {servings && (
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 rounded-lg text-sm text-gray-700">
            👤 Serves {servings}
          </div>
        )}
      </div>

      {/* Allergen warnings */}
      {allergens?.length > 0 && (
        <section className="mb-8 p-4 bg-red-50 border border-red-200 rounded-xl">
          <h2 className="font-semibold text-red-800 mb-3">
            ⚠ Contains allergens
          </h2>
          <div className="flex flex-wrap gap-2">
            {allergens.map((a) => (
              <AllergenBadge
                key={a.id}
                name={a.name}
                displayName={a.display_name}
              />
            ))}
          </div>
        </section>
      )}

      {/* Dietary tags */}
      {dietary_tags?.length > 0 && (
        <section className="mb-8">
          <h2 className="font-semibold text-gray-900 mb-3">Dietary info</h2>
          <div className="flex flex-wrap gap-2">
            {dietary_tags.map((t) => (
              <DietaryBadge
                key={t.id}
                name={t.name}
                displayName={t.display_name}
              />
            ))}
          </div>
        </section>
      )}

      {/* Ingredients */}
      {ingredients?.length > 0 && (
        <section className="mb-8">
          <h2 className="font-semibold text-gray-900 mb-3">Ingredients</h2>
          <ul className="flex flex-col gap-2">
            {ingredients.map((item, index) => (
              <li
                key={index}
                className="flex items-start gap-3 py-2 border-b border-gray-100 last:border-0"
              >
                <span className="w-1.5 h-1.5 rounded-full bg-brand-500 flex-shrink-0 mt-2" />
                <span className="text-sm text-gray-700">
                  {item.ingredient.raw_name}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Link to original */}
      {url && (
        <div className="pt-4 border-t border-gray-200">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-sm text-brand-600 hover:text-brand-700 font-medium transition-colors"
          >
            View full recipe on BBC Good Food →
          </a>
        </div>
      )}

    </main>
  );
}