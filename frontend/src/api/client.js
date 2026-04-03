/*
 * client.js
 *
 * All API calls in one place. Every component that needs data
 * imports from here rather than writing fetch() calls directly.
 *
 * The base URL is /api — nginx strips the /api prefix and
 * forwards the request to the FastAPI container.
 *
 * During local development, Vite's proxy in vite.config.js
 * handles the same forwarding so nginx is not needed locally.
 */

const BASE_URL = "/api";

async function request(path) {
  const response = await fetch(`${BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${path}`);
  }

  return response.json();
}


// ---------------------------------------------------------------
// RECIPES
// ---------------------------------------------------------------

export async function getRecipes({ page = 1, size = 20, cuisine, excludeAllergens, dietaryTags, maxTotalTime } = {}) {
  const params = new URLSearchParams();

  params.set("page", page);
  params.set("size", size);

  if (cuisine)          params.set("cuisine", cuisine);
  if (maxTotalTime)     params.set("max_total_time", maxTotalTime);
  if (excludeAllergens?.length) params.set("exclude_allergens", excludeAllergens.join(","));
  if (dietaryTags?.length)      params.set("dietary_tags", dietaryTags.join(","));

  return request(`/recipes?${params.toString()}`);
}

export async function getRecipeById(id) {
  return request(`/recipes/${id}`);
}

export async function getRecipeAllergens(id) {
  return request(`/recipes/${id}/allergens`);
}

export async function getRecipeDietaryTags(id) {
  return request(`/recipes/${id}/dietary-tags`);
}

export async function getCuisines() {
  return request("/recipes/meta/cuisines");
}


// ---------------------------------------------------------------
// ALLERGENS
// ---------------------------------------------------------------

export async function getAllergens() {
  return request("/allergens");
}


// ---------------------------------------------------------------
// DIETARY TAGS
// ---------------------------------------------------------------

export async function getDietaryTags() {
  return request("/dietary-tags");
}