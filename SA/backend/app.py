from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import google.generativeai as genai
import openai
import requests
import re
import os

# === Load environment variables ===
load_dotenv()

# === Configuration ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_A0PI_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

# === Check API Key Presence ===
if not GOOGLE_API_KEY and not OPENAI_API_KEY:
    raise EnvironmentError("❌ No API key found. Please set GOOGLE_API_KEY or OPENAI_API_KEY in .env")

# === Configure AI APIs ===
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

# === Flask & Scheduler Setup ===
app = Flask(__name__)
CORS(app)
scheduler = BackgroundScheduler()
scheduler.start()

# === AI Model Handler ===
def generate_ai_content(prompt, model="gemini"):
    try:
        if model == "gemini":
            if not GOOGLE_API_KEY:
                return "❌ Gemini API key not configured"
            return genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt).text.strip()
        elif model == "openai":
            if not OPENAI_API_KEY:
                return "❌ OpenAI API key not configured"
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content.strip()
        else:
            return f"❌ Unsupported model: {model}"
    except Exception as e:
        return f"❌ Error: {e}"

# === Generate Post Content ===
def generate_post_content(idea, theme, model_choice="gemini"):
    prompt = f"""
Using the content idea: "{idea}" under the theme "{theme}", create a social media post.

Include:
[CONTENT]: 2-4 line Instagram post
[HASHTAGS]: 5-10 relevant hashtags
[CTA]: A strong call to action
"""
    output = generate_ai_content(prompt, model_choice)

    sections = {"CONTENT": "", "HASHTAGS": "", "CTA": ""}
    current = None
    for line in output.splitlines():
        line = line.strip()
        if "[CONTENT]" in line.upper():
            current = "CONTENT"
        elif "[HASHTAGS]" in line.upper():
            current = "HASHTAGS"
        elif "[CTA]" in line.upper():
            current = "CTA"
        elif current:
            sections[current] += line + " "
    return sections

@app.route("/generate_post", methods=["POST"])
def generate_post():
    data = request.get_json()
    idea = data.get("idea", "")
    theme = data.get("theme", "")
    model = data.get("model", "gemini")
    return jsonify(generate_post_content(idea, theme, model))

# === Generate Calendar ===
def generate_calendar(theme, model_choice="gemini"):
    base_date = datetime.now()
    weekdays = {
        0: "Monday Motivation",
        1: "Tech Tuesday",
        2: "Work in Progress Wednesday",
        3: "Throwback Thursday",
        4: "Feature Friday",
        5: "Behind the Scenes Saturday",
        6: "Sunday Q&A"
    }

    dates = [base_date + timedelta(days=i) for i in range(30)]
    prompts = [
        f"{i+1}. Creative Instagram idea for theme '{theme}' on '{weekdays[date.weekday()]}' ({date.strftime('%A %Y-%m-%d')})"
        for i, date in enumerate(dates)
    ]

    try:
        output = generate_ai_content("Give 30 short creative Instagram post ideas:\n" + "\n".join(prompts), model_choice)
        raw_ideas = output.strip().split("\n")
        ideas = [re.sub(r"^\d+\.\s*", "", line.strip()) for line in raw_ideas if line.strip()]
    except Exception as e:
        ideas = [f"Error: {e}"] * 30

    calendar = []
    for i, date in enumerate(dates):
        idea_text = ideas[i] if i < len(ideas) else "No idea generated"
        calendar.append({
            "date": date.strftime("%Y-%m-%d"),
            "day": date.strftime("%A"),
            "weekly_theme": weekdays[date.weekday()],
            "post_idea": idea_text,
            "theme": theme,
            "approved": False
        })
    return calendar

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    theme = data.get("theme", "").strip()
    model = data.get("model", "gemini")
    if not theme:
        return jsonify({"error": "Theme is required"}), 400
    return jsonify(generate_calendar(theme, model))

# === Google Image Search ===
def fetch_google_image(query):
    try:
        keyword = re.sub(r'[^a-zA-Z0-9 ]', '', query.split('.')[0])[:50]
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": keyword,
            "key": GOOGLE_CSE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "searchType": "image",
            "imgType": "photo",
            "imgSize": "large",
            "num": 3,
            "safe": "active"
        }
        res = requests.get(url, params=params)
        data = res.json()
        if "items" in data:
            return data["items"][0]["link"]
    except Exception as e:
        print("❌ Image fetch error:", e)
    return None

@app.route("/search_image", methods=["POST"])
def search_image():
    data = request.get_json()
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query is required"}), 400
    image_url = fetch_google_image(query)
    if image_url:
        return jsonify({"image_url": image_url})
    return jsonify({"error": "No image found"}), 404

# === Post to Instagram ===
def post_to_instagram(image_url, caption):
    try:
        media_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": ACCESS_TOKEN
        }
        media_res = requests.post(media_url, data=payload).json()
        creation_id = media_res.get("id")
        if not creation_id:
            return {"error": "❌ Failed to create media", "details": media_res}

        publish_url = f"https://graph.facebook.com/v18.0/{IG_USER_ID}/media_publish"
        publish_res = requests.post(publish_url, data={
            "creation_id": creation_id,
            "access_token": ACCESS_TOKEN
        }).json()

        if publish_res.get("id"):
            return {
                "message": "✅ Post published successfully",
                "media_id": creation_id,
                "publish_response": publish_res
            }
        else:
            return {"error": "❌ Failed to publish media", "details": publish_res}
    except Exception as e:
        return {"error": str(e)}

@app.route("/auto_post", methods=["POST"])
def auto_post():
    try:
        data = request.get_json()
        idea = data.get("idea", "")
        image_url = data.get("image_url", "")
        model = data.get("model", "gemini")

        prompt = f"""
Write an Instagram caption for the idea: "{idea}".
Include 5 relevant hashtags and a short call to action.
Output clean caption text with hashtags at the end.
"""
        caption = generate_ai_content(prompt, model)
        result = post_to_instagram(image_url, caption)

        if "error" in result:
            return jsonify(result), 500
        return jsonify({
            "message": result["message"],
            "caption": caption,
            "media_id": result["media_id"],
            "response": result["publish_response"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/schedule_post", methods=["POST"])
def schedule_post():
    try:
        data = request.get_json()
        idea = data.get("idea", "")
        image_url = data.get("image_url", "")
        schedule_time = data.get("schedule_time")
        model = data.get("model", "gemini")

        prompt = f"""
Write an Instagram caption for the idea: "{idea}".
Include 5 relevant hashtags and a short call to action.
Output clean caption text with hashtags at the end.
"""
        caption = generate_ai_content(prompt, model)
        run_time = datetime.fromisoformat(schedule_time).replace(second=0)
        job_id = f"job_{datetime.now().timestamp()}"

        scheduler.add_job(
            func=post_to_instagram,
            trigger='date',
            run_date=run_time,
            args=[image_url, caption],
            id=job_id
        )

        return jsonify({
            "message": f"✅ Post scheduled for {run_time.strftime('%Y-%m-%d %H:%M')}",
            "job_id": job_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Start Server ===
if __name__ == "__main__":
    app.run(debug=True)
