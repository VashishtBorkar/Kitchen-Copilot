import type { RecipeSearchResponse } from "@/types/recipes";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function searchRecipes(query: string): Promise<RecipeSearchResponse> {
  const response = await fetch(`${apiBaseUrl}/api/search`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      limit: 10,
    }),
  });

  if (!response.ok) {
    throw new Error(`Search request failed with status ${response.status}`);
  }

  return response.json() as Promise<RecipeSearchResponse>;
}
