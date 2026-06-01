"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { searchRecipes } from "@/lib/api";
import type { RecipeSearchResult } from "@/types/recipes";

const exampleQueries = [
  "High protein Asian-inspired dinner",
  "Quick weeknight chicken meal",
  "Healthy comfort food under 600 calories",
];

export default function HomePage() {
  const [query, setQuery] = useState(exampleQueries[0]);
  const [results, setResults] = useState<RecipeSearchResult[]>([]);
  const [status, setStatus] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setStatus("");

    try {
      const response = await searchRecipes(query);
      setResults(response.results);
      if (response.results.length === 0) {
        setStatus("No recipes returned yet. Ingestion and semantic search are next.");
      }
    } catch {
      setResults([]);
      setStatus("Search API is not ready yet. Backend scaffold is in place for /api/search.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <strong>KitchenCopilot</strong>
          <span>Retrieval-first recipe recommendations</span>
        </div>
      </header>

      <section className="search-panel">
        <h1>Find recipes by intent, ingredients, and cooking goals.</h1>
        <p className="muted">
          The MVP will use semantic retrieval, deterministic ranking, and ingredient reasoning
          before any LLM-powered adaptation is introduced.
        </p>

        <form className="search-form" onSubmit={handleSubmit}>
          <input
            aria-label="Recipe search query"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try: spicy shrimp bowl"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Searching..." : "Search"}
          </button>
        </form>

        <div className="tag-row" aria-label="Example searches">
          {exampleQueries.map((example) => (
            <button
              className="pill"
              key={example}
              onClick={() => setQuery(example)}
              type="button"
            >
              {example}
            </button>
          ))}
        </div>
      </section>

      {status ? <p className="status">{status}</p> : null}

      <section className="results" aria-label="Recipe search results">
        {results.map((recipe) => (
          <article className="recipe-card" key={recipe.id}>
            <h2>
              <Link href={`/recipes/${recipe.id}`}>{recipe.title}</Link>
            </h2>
            <div className="meta-row">
              {recipe.cuisine ? <span className="pill">{recipe.cuisine}</span> : null}
              {recipe.prepTimeMinutes ? (
                <span className="pill">{recipe.prepTimeMinutes} min</span>
              ) : null}
              {typeof recipe.score === "number" ? (
                <span className="pill">Score {recipe.score.toFixed(2)}</span>
              ) : null}
            </div>
            {recipe.summary ? <p className="muted">{recipe.summary}</p> : null}
          </article>
        ))}
      </section>
    </main>
  );
}
