import requests
from sqlalchemy.orm import Session
from app.models.blog import Blog
from app.models.category import Category
import os
import json
import re

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def generate_blog_for_category(category, db: Session):

    prompt = f"""
    Write a detailed comparison blog for category: {category.category_name}

    Return ONLY valid JSON.

    {{
      "title": "blog title",
      "content": "full blog article in markdown",
      "winner_name": "winning product",
      "winner_margin": number
    }}
    """

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek/deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    ai_text = response.json()["choices"][0]["message"]["content"]

    # ✅ Extract JSON safely
    json_match = re.search(r"\{.*\}", ai_text, re.DOTALL)

    if not json_match:
        print("Invalid AI response:", ai_text)
        return

    data = json.loads(json_match.group())

    title = data.get("title", f"{category.category_name} Comparison")
    content = data.get("content", "")
    winner = data.get("winner_name", "Unknown")
    margin = float(data.get("winner_margin", 10))

    # Better slug
    slug = title.lower().replace(" ", "-").replace("&", "").replace("--", "-")

    blog = Blog(
        category_id=category.id,
        title=title,
        slug=slug,
        summary=f"Detailed comparison of {category.category_name}.",
        content=content,
        winner_name=winner,
        winner_margin=margin,
        image_url=category.image_url
    )

    db.add(blog)
    db.commit()


def generate_daily_blogs(db: Session):

    categories = db.query(Category).order_by(Category.id).all()

    selected = categories[:3]

    for category in selected:
        try:
            generate_blog_for_category(category, db)
        except Exception as e:
            print("Blog generation failed:", e)