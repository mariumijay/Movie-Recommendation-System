# %%
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import math

# %%
movies = pd.read_csv("movies.csv")

# %%
def load_raw(path: str = "movies.csv") -> pd.DataFrame:
    """Read CSV and keep only the columns we need."""
    df = pd.read_csv(path)

    # Core content columns (your notebook selection)
    content_cols = [
        "id", "genres", "keywords", "original_language",
        "title", "overview", "tagline", "cast", "director",
    ]
    # Extra columns for rating-based filtering / trending
    extra_cols = [c for c in ["vote_average", "vote_count", "release_date"]
                  if c in df.columns]

    keep = [c for c in content_cols + extra_cols if c in df.columns]
    return df[keep].copy()

# %%
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Steps (from notebook):
      1. Combine text columns into 'tags'
      2. Drop source columns
      3. Fill missing values
      4. Remove duplicates
      5. Lowercase titles
      6. Build 'content' = genres + tags
    """
    df = df.copy()

    # Step 1: tags = keywords + overview + tagline + cast + director
    text_parts = ["keywords", "overview", "tagline", "cast", "director"]
    available  = [c for c in text_parts if c in df.columns]
    df["tags"]  = df[available].fillna("").apply(
        lambda row: " ".join(row.values.astype(str)), axis=1
    )

    # Step 2: drop source columns
    drop_cols = [c for c in ["cast", "director", "keywords",
                              "overview", "tagline", "original_language"]
                 if c in df.columns]
    df = df.drop(columns=drop_cols)

    # Step 3: fill missing values
    df["genres"] = df["genres"].fillna("NO genre")
    df["tags"]   = df["tags"].fillna("NO information")
    if "vote_average" in df.columns:
        df["vote_average"] = pd.to_numeric(
            df["vote_average"], errors="coerce").fillna(0.0)
    if "vote_count" in df.columns:
        df["vote_count"] = pd.to_numeric(
            df["vote_count"], errors="coerce").fillna(0)

    # Step 4: remove duplicates
    df = df.drop_duplicates().reset_index(drop=True)

    # Step 5: lowercase titles
    df["title"] = df["title"].str.lower().str.strip()

    # Step 6: content = genres + tags
    df["content"] = df["genres"].fillna("") + " " + df["tags"].fillna("")

    return df

# %%
def build_model(df: pd.DataFrame):
    """
    Fit TF-IDF on 'content' column and compute cosine similarity matrix.
    Returns (tfidf_vectorizer, similarity_matrix).
    """
    tfidf        = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform(df["content"])
    similarity   = cosine_similarity(tfidf_matrix)
    return tfidf, similarity

# %%
def recommendor(
    user_input: str,
    df: pd.DataFrame,
    similarity_matrix,
    top_n: int = 10,
    min_rating: float = 0.0,
):
    # Normalise input
    user_input = user_input.strip().lower()

    # Find movie row
    movie_row = df[df["title"] == user_input]
    if movie_row.empty:
        return "not_found"

    movie_index = movie_row.index[0]

    # Build (index, score) pairs
    row       = similarity_matrix[movie_index]
    sim_score = [(i, float(row[i])) for i in range(len(row))]

    # ── Selection sort (your original algorithm) ──
    for i in range(len(sim_score)):
        max_idx = i
        for j in range(i + 1, len(sim_score)):
            if sim_score[j][1] > sim_score[max_idx][1]:
                max_idx = j
        sim_score[i], sim_score[max_idx] = sim_score[max_idx], sim_score[i]

    # Skip self, apply rating filter, collect top_n
    recommendations = []
    for idx, score in sim_score:
        if idx == movie_index:
            continue
        row_data = df.iloc[idx]
        vote_avg = float(row_data.get("vote_average", 0))
        if vote_avg < min_rating:
            continue
        recommendations.append({
            "title":        row_data["title"].title(),
            "vote_average": vote_avg,
            "genres":       str(row_data.get("genres", "")),
            "release_date": str(row_data.get("release_date", "")),
            "id":           row_data.get("id", ""),
            "sim_score":    round(score, 4),
        })
        if len(recommendations) >= top_n:
            break

    return recommendations

# %%
def get_trending(df: pd.DataFrame, n: int = 10):
    """Return top-n trending movies by weighted popularity score."""
    work = df.copy()
    if "vote_count" in work.columns:
        work["trend_score"] = work["vote_average"] * work["vote_count"].apply(
            lambda c: math.log10(float(c) + 1)
        )
    else:
        work["trend_score"] = work["vote_average"]

    top    = work.nlargest(n, "trend_score")
    result = []
    for _, row in top.iterrows():
        result.append({
            "title":        str(row["title"]).title(),
            "vote_average": float(row.get("vote_average", 0)),
            "genres":       str(row.get("genres", "")),
            "release_date": str(row.get("release_date", "")),
            "id":           row.get("id", ""),
        })
    return result



# %%
def search_suggestions(query: str, df: pd.DataFrame, n: int = 6):
    """Return up to n titles that contain the query substring."""
    q = query.strip().lower()
    if not q:
        return []
    mask = df["title"].str.contains(q, na=False)
    return [t.title() for t in df.loc[mask, "title"].head(n)]

# %%
def build_pipeline(path: str = "movies.csv"):
    """
    Full pipeline: load → preprocess → build model.
    Returns (df, similarity_matrix) ready for the Streamlit app.
    """
    raw       = load_raw(path)
    df        = preprocess(raw)
    _, sim    = build_model(df)
    return df, sim


