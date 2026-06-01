import Link from "next/link";

type RecipeDetailPageProps = {
  params: {
    id: string;
  };
};

export default function RecipeDetailPage({ params }: RecipeDetailPageProps) {
  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <strong>Recipe detail</strong>
          <span>Recipe id: {params.id}</span>
        </div>
        <Link className="link-button" href="/">
          Back to search
        </Link>
      </header>

      <section className="search-panel">
        <h1>Recipe details will render here after ingestion is connected.</h1>
        <p className="muted">
          This route is intentionally scaffolded now so the frontend has a stable place for
          ingredients, instructions, nutrition, substitutions, and customization controls.
        </p>
      </section>
    </main>
  );
}
