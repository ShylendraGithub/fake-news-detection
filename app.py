from flask import Flask, render_template, request
import requests

from summarizer import summarize_articles

app = Flask(__name__)
app.secret_key = "you-did-it"

KEY = "KEY"
CX  = "Key"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        claim = request.form.get("claim", "").strip()
        if not claim:
            return render_template("index.html", result=None)

        search_query = claim.replace("$", "").replace(",", "").replace("100,000", "100000 OR 100k OR 100000")

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": f'"{claim}"',   
                "key": KEY,
                "cx": CX,
                "num": 10
            }

            data = requests.get(url, params=params, timeout=12).json()
            items = data.get("items", [])
            count = len(items)
            snippets = [item.get("snippet", "") for item in items]

            summary = summarize_articles(snippets)

            if count >= 5:
                verdict, color = "REAL", "#10b981"
            elif count >= 1:
                verdict, color = "VERIFIED", "#22c55e"
            else:
                verdict, color = "NOT VERIFIED", "#ef4444"

            sources = []
            for item in items:
                domain = item.get("displayLink", "").replace("www.", "").split(".")[0].upper()
                sources.append(domain)
            sources = list(dict.fromkeys(sources))

            result = {
                "verdict": verdict,
                "color": color,
                "claim": claim,
                "explanation": f"Found in {count} trusted news source{'s' if count != 1 else ''}",
                "sources": sources or ["None"],
                "credibility_score": 98 if count >= 5 else 75 if count >= 1 else 5,

                "summary": summary,

                "article_count": count
            }

        except Exception as e:
            result = {
                "verdict": "ERROR",
                "color": "#ef4444",
                "explanation": f"API Error: {str(e)}",
                "claim": claim
            }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
