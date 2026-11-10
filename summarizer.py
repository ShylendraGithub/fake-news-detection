from transformers import pipeline
try:
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn"
    )
except Exception as e:
    print(f"[WARNING] Could not load BART model: {e}")
    print("Summarization will be disabled.")
    summarizer = None

def summarize_articles(article_texts):
    if not article_texts or len(article_texts) == 0:
        return "No relevant articles found to summarize."

    cleaned = []
    for text in article_texts:
        if isinstance(text, str):
            text = text.strip()
            if text:
                cleaned.append(text)

    if not cleaned:
        return "No valid article content for summarization."

    full_text = " ".join(cleaned)

    if len(full_text) > 2500:
        full_text = full_text[:2500] + "..."
   
    if summarizer is None:
        return "Summary unavailable (summarization model not loaded)."

    try:
        result = summarizer(
            full_text,
            max_length=200,
            min_length=70,
            do_sample=False,
            truncation=True,                  
            clean_up_tokenization_spaces=True
        )
        summary = result[0]["summary_text"].strip()

       
        if summary and summary[0].isalpha() and summary[0].islower():
            summary = summary[0].upper() + summary[1:]
        if summary and summary[-1] not in ".!?":
            summary += "."

        return summary

    except Exception as e:
        return "Summary temporarily unavailable due to processing limits."