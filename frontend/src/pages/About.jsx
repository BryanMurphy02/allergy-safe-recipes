/*
 * About.jsx
 *
 * A simple static page explaining what SafePlate does,
 * which allergens are tracked, and what the dietary tags mean.
 */

import { Link } from "react-router-dom";

const ALLERGENS = [
  { name: "Peanuts", description: "Includes peanuts, peanut butter, peanut oil, and groundnut oil." },
  { name: "Tree Nuts", description: "Includes almonds, cashews, walnuts, pecans, pistachios, hazelnuts, and coconut." },
  { name: "Dairy", description: "Includes milk, cream, butter, cheese, yoghurt, and all milk-derived ingredients." },
  { name: "Egg", description: "Includes whole eggs, egg yolks, egg whites, mayonnaise, and hollandaise." },
];

const DIETARY_TAGS = [
  { name: "Vegetarian", description: "Contains no meat or fish." },
  { name: "Vegan", description: "Contains no animal products of any kind." },
  { name: "Gluten-Free", description: "Contains no gluten-containing ingredients such as wheat, barley, or rye." },
  { name: "Contains Raw Egg", description: "Contains raw or lightly cooked egg — relevant for vulnerable groups." },
];

export default function About() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-12">

      {/* Hero */}
      <div className="mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">About SafePlate</h1>
        <p className="text-gray-600 leading-relaxed text-lg">
          SafePlate scrapes recipes from BBC Good Food and analyses every
          ingredient for allergens and dietary suitability. Use the filters
          on the recipes page to find meals that are safe for your needs.
        </p>
      </div>

      {/* How it works */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">How it works</h2>
        <div className="flex flex-col gap-4">
          {[
            { step: "1", title: "Recipes are scraped", body: "A scraper runs daily and pulls new recipes from BBC Good Food using their structured recipe data." },
            { step: "2", title: "Ingredients are analysed", body: "Each ingredient is checked against a lookup table of known allergen-containing foods." },
            { step: "3", title: "Dietary tags are applied", body: "The full ingredient list is checked to determine whether the recipe is vegetarian, vegan, or gluten-free." },
            { step: "4", title: "You filter safely", body: "Use the filters to exclude allergens or require dietary tags — the results update instantly." },
          ].map(({ step, title, body }) => (
            <div key={step} className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center text-sm font-bold flex-shrink-0 mt-0.5">
                {step}
              </div>
              <div>
                <h3 className="font-medium text-gray-900">{title}</h3>
                <p className="text-sm text-gray-500 mt-0.5">{body}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Tracked allergens */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Tracked allergens</h2>
        <div className="grid grid-cols-1 gap-3">
          {ALLERGENS.map(({ name, description }) => (
            <div key={name} className="flex gap-3 p-4 bg-red-50 border border-red-100 rounded-xl">
              <span className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0 mt-1.5" />
              <div>
                <p className="font-medium text-red-800">{name}</p>
                <p className="text-sm text-red-600 mt-0.5">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Dietary tags */}
      <section className="mb-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Dietary tags</h2>
        <div className="grid grid-cols-1 gap-3">
          {DIETARY_TAGS.map(({ name, description }) => (
            <div key={name} className="flex gap-3 p-4 bg-green-50 border border-green-100 rounded-xl">
              <span className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0 mt-1.5" />
              <div>
                <p className="font-medium text-green-800">{name}</p>
                <p className="text-sm text-green-600 mt-0.5">{description}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer */}
      <section className="p-4 bg-amber-50 border border-amber-200 rounded-xl mb-12">
        <h2 className="font-semibold text-amber-800 mb-2">Important disclaimer</h2>
        <p className="text-sm text-amber-700 leading-relaxed">
          SafePlate uses automated ingredient analysis which may not catch every
          allergen. Always check the original recipe and ingredient labels before
          cooking, especially if you have a severe allergy. SafePlate is a
          convenience tool and should not be your only safety check.
        </p>
      </section>

      {/* CTA */}
      <div className="text-center">
        <Link
          to="/"
          className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-medium px-6 py-3 rounded-xl transition-colors"
        >
          Browse recipes
        </Link>
      </div>

    </main>
  );
}