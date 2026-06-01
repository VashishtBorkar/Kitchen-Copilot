export type RecipeSearchResult = {
  id: string;
  title: string;
  summary?: string;
  cuisine?: string;
  prepTimeMinutes?: number;
  score?: number;
  tags?: string[];
  nutrition?: {
    calories?: number;
    proteinGrams?: number;
    carbsGrams?: number;
    fatGrams?: number;
  };
};

export type RecipeSearchResponse = {
  query: string;
  results: RecipeSearchResult[];
};
