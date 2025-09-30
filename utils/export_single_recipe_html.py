import tempfile
import webbrowser


def export_single_recipe_html(recipe, open_after=True):
    """Export a single recipe dictionary to HTML and open it in browser."""
    html = f"""
    <html>
    <head>
        <title>{recipe['title']}</title>
        <meta charset="utf-8"/>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 2em; }}
            h1 {{ color: #3b7; }}
            .section {{ margin-bottom: 1.5em; }}
            .meta {{ color: #666; font-size: 0.95em; }}
        </style>
    </head>
    <body>
        <h1>{recipe['title']}</h1>
        <div class="meta">
            Source: {recipe.get('source','')}<br/>
            URL: {recipe.get('url','')}<br/>
            Tags: {recipe.get('tags','')}<br/>
            Rating: {recipe.get('rating',0)}<br/>
            Servings: {recipe.get('servings','')}
        </div>
        <div class="section">
            <h2>Ingredients</h2>
            <pre>{recipe.get('ingredients','')}</pre>
        </div>
        <div class="section">
            <h2>Instructions</h2>
            <pre>{recipe.get('instructions','')}</pre>
        </div>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
        f.write(html)
        html_path = f.name

    if open_after:
        webbrowser.open(f"file://{html_path}")
