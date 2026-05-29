# KitchenCopilot

KitchenCopilot is an AI-powered cooking recommendation platform designed to help users discover meals that match their preferences, dietary goals, and cooking needs.

Unlike traditional recipe websites that rely on keyword search, KitchenCopilot uses semantic search and recommendation techniques to understand natural language queries and surface relevant recipes. Users can search for meals using descriptions such as:

* "High protein Asian-inspired dinner"
* "Spicy pasta dish"
* "Healthy shrimp meal under 600 calories"
* "Quick weeknight chicken recipe"

The long-term vision is to build an intelligent cooking assistant that combines recipe retrieval, ingredient reasoning, personalization, and AI-powered recipe adaptation.

---

## Core Features

### Semantic Recipe Search

KitchenCopilot uses embedding-based semantic search to retrieve recipes based on user intent rather than exact keyword matches.

Examples:

* "High protein Asian-inspired"
* "Healthy comfort food"
* "Easy meal prep lunch"
* "Spicy shrimp bowl"

Recipes are ranked using a combination of semantic similarity, nutrition information, and personalization signals.

---

### Ingredient Substitution Engine

KitchenCopilot includes an ingredient substitution system that helps users find alternatives when they are missing ingredients.

The substitution engine uses ingredient metadata such as:

* Category
* Flavor profile
* Cuisine associations
* Common replacement relationships

Examples:

* Mirin → Rice vinegar + sugar
* Sour cream → Greek yogurt
* Chicken thighs → Chicken breast

The goal is to provide practical, context-aware substitutions that preserve the intent of the recipe.

---

### Recipe Personalization

Users can modify recipes based on common cooking goals.

Supported personalization goals may include:

* Higher protein
* Lower calorie
* Vegetarian
* Vegan
* Gluten-free
* Dairy-free

Personalization is driven by a rule-based transformation engine that applies ingredient swaps and recipe modifications while maintaining recipe quality.

---

### LLM-Powered Recipe Adaptation (Future)

Future versions of KitchenCopilot will include optional LLM-powered features that build on top of the retrieval and personalization systems.

Potential capabilities include:

* Rewriting recipes after modifications
* Adapting recipes to pantry constraints
* Explaining ingredient substitutions
* Generating customized cooking instructions
* Creating personalized meal plans

The LLM is intended to serve as a reasoning and explanation layer rather than the primary source of recipe generation.

---

## Technical Goals

KitchenCopilot is designed to explore several areas of AI and recommendation systems:

* Semantic retrieval
* Embedding-based search
* Recommendation systems
* Personalization
* Ingredient reasoning
* Knowledge representation
* AI-assisted workflow design

The project prioritizes deterministic retrieval and recommendation pipelines first, with LLM functionality layered on top where it provides meaningful value.

---

## Project Status

Currently in active development.

Planned milestones:

1. Recipe database and ingestion pipeline
2. Embedding generation and semantic search
3. Recipe ranking and retrieval API
4. Ingredient substitution engine
5. Recipe personalization system
6. User preferences and recommendation improvements
7. LLM-powered recipe adaptation and meal planning
