import os
import json
import uuid
import time
import sqlite3
import secrets
import urllib.parse
import datetime
import io
from pathlib import Path
from typing import Optional, List, Dict, Any
from zoneinfo import ZoneInfo

import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image, ImageDraw, ImageFont




load_dotenv()

DB_PATH = os.getenv("DB_PATH", "tokens.db")
META_GRAPH_BASE = "https://graph.facebook.com/v19.0"
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
BACKEND_PUBLIC_BASE = os.getenv("BACKEND_PUBLIC_BASE", "http://localhost:8000").rstrip("/")
DEV_TOKEN = os.getenv("DEV_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SDXL_PROVIDER = os.getenv("SDXL_PROVIDER", "replicate")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
REPLICATE_SDXL_MODEL_VERSION = os.getenv("REPLICATE_SDXL_MODEL_VERSION")

BRAND_NAME = os.getenv("BRAND_NAME", "Postify")
BRAND_PRIMARY = os.getenv("BRAND_PRIMARY", "#0f172a")
BRAND_SECONDARY = os.getenv("BRAND_SECONDARY", "#334155")
BRAND_ACCENT = os.getenv("BRAND_ACCENT", "#22c55e")
FONT_PATH = os.getenv("FONT_PATH", "")

DEFAULT_TZ = os.getenv("DEFAULT_TZ", "Asia/Kolkata")

LINKEDIN_AUTHOR_URN = os.getenv("LINKEDIN_AUTHOR_URN")

OAUTH_STATE_TTL_SECONDS = 10 * 60



app = FastAPI(title="Postify API")

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        o.strip()
        for o in (os.getenv("FRONTEND_ORIGIN", "http://localhost:3000,http://127.0.0.1:3000") or "").split(",")
        if o.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            access_token TEXT NOT NULL,
            meta JSON,
            UNIQUE(user_id, platform)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS oauth_states (
            state TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            meta JSON
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS blog_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            excerpt TEXT,
            hero_image_url TEXT,
            tags JSON,
            published_at TEXT,
            created_at INTEGER NOT NULL,
            UNIQUE(user_id, url)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS content_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blog_post_id INTEGER NOT NULL,
            captions JSON NOT NULL,
            prompts JSON,
            images JSON,
            created_at INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blog_post_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            scheduled_at INTEGER NOT NULL,
            status TEXT NOT NULL,
            content TEXT,
            image_path TEXT,
            external_id TEXT,
            error TEXT,
            created_at INTEGER NOT NULL
        )
        """
    )

    con.commit()
    con.close()


def create_oauth_state(user_id: str, platform: str) -> str:
    state = secrets.token_urlsafe(32)
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO oauth_states (state, user_id, platform, created_at, meta) VALUES (?, ?, ?, ?, ?)",
        (state, user_id, platform, _now_ts(), "{}"),
    )
    con.commit()
    con.close()
    return state


def consume_oauth_state(state: str, platform: str) -> Dict[str, Any]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT user_id, platform, meta, created_at FROM oauth_states WHERE state = ? AND platform = ?",
        (state, platform),
    )
    row = cur.fetchone()
    con.close()
    if not row:
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    created_at = row[2]
    if _now_ts() - created_at > OAUTH_STATE_TTL_SECONDS:
        raise HTTPException(status_code=400, detail="State expired")
    return {"user_id": row[0], "platform": row[1], "meta": json.loads(row[3] or "{}")}


def get_meta_oauth_config() -> tuple[str, str, str]:
    app_id = os.getenv("META_APP_ID") or os.getenv("FB_APP_ID")
    app_secret = os.getenv("META_APP_SECRET") or os.getenv("FB_APP_SECRET")
    redirect_uri = os.getenv("META_REDIRECT_URI")
    if not app_id or not app_secret or not redirect_uri:
        raise HTTPException(status_code=400, detail="Missing META_APP_ID/META_APP_SECRET/META_REDIRECT_URI")
    return app_id, app_secret, redirect_uri


def exchange_meta_code_for_token(code: str) -> str:
    app_id, app_secret, redirect_uri = get_meta_oauth_config()
    url = f"{META_GRAPH_BASE}/oauth/access_token"
    resp = requests.get(
        url,
        params={
            "client_id": app_id,
            "client_secret": app_secret,
            "redirect_uri": redirect_uri,
            "code": code,
        },
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}
    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail={"platform": "meta", "error": data})
    token = data.get("access_token")
    if not token:
        raise HTTPException(status_code=400, detail={"platform": "meta", "error": "Missing access_token in response"})
    return str(token)


def get_facebook_page_access_token(user_access_token: str, page_id: str) -> str:
    url = f"{META_GRAPH_BASE}/{page_id}"
    resp = requests.get(
        url,
        params={
            "fields": "access_token",
            "access_token": user_access_token,
        },
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}
    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail={"platform": "facebook", "error": data})
    page_token = data.get("access_token")
    if not page_token:
        raise HTTPException(status_code=400, detail={"platform": "facebook", "error": "Missing page access token"})
    return str(page_token)


@app.post("/automation/blog/webhook")
def automation_blog_webhook(payload: Dict[str, Any], background_tasks: BackgroundTasks):
    """Called by your custom website when a blog post is published."""
    blog_post_id = _insert_blog_post(payload)
    background_tasks.add_task(process_blog_post, blog_post_id)
    return {"status": "accepted", "blog_post_id": blog_post_id}


@app.get("/automation/blog/recent")
def automation_recent_blog_posts(user_id: str, limit: int = 20):
    limit = max(1, min(int(limit), 50))
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, url, title, published_at, created_at
        FROM blog_posts
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cur.fetchall()
    con.close()
    return {
        "items": [
            {
                "id": r[0],
                "url": r[1],
                "title": r[2],
                "published_at": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]
    }


@app.get("/automation/scheduled")
def automation_scheduled_posts(user_id: str, limit: int = 50):
    limit = max(1, min(int(limit), 200))
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        SELECT id, blog_post_id, platform, scheduled_at, status, external_id, error
        FROM scheduled_posts
        WHERE user_id = ?
        ORDER BY scheduled_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cur.fetchall()
    con.close()
    return {
        "items": [
            {
                "id": r[0],
                "blog_post_id": r[1],
                "platform": r[2],
                "scheduled_at": r[3],
                "status": r[4],
                "external_id": r[5],
                "error": r[6],
            }
            for r in rows
        ]
    }


@app.on_event("startup")
def on_startup():
    init_db()

    scheduler = BackgroundScheduler(timezone=ZoneInfo(DEFAULT_TZ))
    scheduler.add_job(publish_due_scheduled_posts, "interval", seconds=30)
    scheduler.start()


def _hex_to_rgb(h: str):
    h = (h or "").strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    if len(h) != 6:
        return (15, 23, 42)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _load_font(size: int) -> ImageFont.ImageFont:
    try:
        if FONT_PATH and Path(FONT_PATH).exists():
            return ImageFont.truetype(FONT_PATH, size=size)
    except Exception:
        pass
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def _now_ts() -> int:
    return int(time.time())


def _peak_time_for(platform: str, base_dt: datetime.datetime) -> datetime.datetime:
    platform = platform.lower().strip()
    weekday = base_dt.weekday()

    if platform == "linkedin":
        if weekday >= 5:
            days = (7 - weekday) % 7
            if days == 0:
                days = 1
            base_dt = base_dt + datetime.timedelta(days=days)
        return base_dt.replace(hour=9, minute=45, second=0, microsecond=0)

    if platform == "twitter":
        return base_dt.replace(hour=9, minute=30, second=0, microsecond=0) if base_dt.hour < 12 else base_dt.replace(hour=18, minute=0, second=0, microsecond=0)

    if platform == "instagram":
        return base_dt.replace(hour=12, minute=0, second=0, microsecond=0) if base_dt.hour < 12 else base_dt.replace(hour=19, minute=30, second=0, microsecond=0)

    if platform == "facebook":
        return base_dt.replace(hour=13, minute=0, second=0, microsecond=0) if base_dt.hour < 12 else base_dt.replace(hour=19, minute=0, second=0, microsecond=0)

    return base_dt.replace(hour=12, minute=0, second=0, microsecond=0)


def _generate_captions_openai(title: str, url: str, excerpt: str, tags: List[str]) -> Dict[str, Any]:
    if not OPENAI_API_KEY:
        return {
            "instagram": {"caption": f"{title}\n\n{excerpt}\n\nRead: {url}", "hashtags": ["#blog", "#marketing"]},
            "facebook": {"caption": f"{title}\n\n{excerpt}\n\nRead: {url}", "hashtags": ["#blog"]},
            "twitter": {"caption": f"{title}\n\n{url}", "hashtags": ["#marketing"]},
            "linkedin": {"caption": f"{title}\n\n{excerpt}\n\nRead: {url}", "hashtags": ["#marketing"]},
        }

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = {
        "brand": BRAND_NAME,
        "title": title,
        "url": url,
        "excerpt": excerpt,
        "tags": tags,
        "rules": [
            "Do not invent facts or statistics.",
            "Keep X (Twitter) concise and high-engagement.",
            "Return JSON only.",
        ],
        "output_schema": {
            "instagram": {"caption": "string", "hashtags": ["string"]},
            "facebook": {"caption": "string", "hashtags": ["string"]},
            "twitter": {"caption": "string", "hashtags": ["string"]},
            "linkedin": {"caption": "string", "hashtags": ["string"]},
        },
    }

    res = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a social media strategist."},
            {"role": "user", "content": json.dumps(prompt)},
        ],
        temperature=0.7,
    )

    content = res.choices[0].message.content
    try:
        return json.loads(content)
    except Exception:
        return {
            "instagram": {"caption": f"{title}\n\n{excerpt}\n\nRead: {url}", "hashtags": ["#blog", "#marketing"]},
            "facebook": {"caption": f"{title}\n\n{excerpt}\n\nRead: {url}", "hashtags": ["#blog"]},
            "twitter": {"caption": f"{title}\n\n{url}", "hashtags": ["#marketing"]},
            "linkedin": {"caption": f"{title}\n\n{excerpt}\n\nRead: {url}", "hashtags": ["#marketing"]},
        }


def _replicate_sdxl_generate(prompt: str) -> Optional[bytes]:
    if not REPLICATE_API_TOKEN or not REPLICATE_SDXL_MODEL_VERSION:
        return None

    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }

    create = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers=headers,
        json={
            "version": REPLICATE_SDXL_MODEL_VERSION,
            "input": {
                "prompt": prompt,
                "width": 1080,
                "height": 1350,
                "num_outputs": 1,
            },
        },
        timeout=60,
    )
    if create.status_code >= 400:
        return None
    pred = create.json()
    pred_url = pred.get("urls", {}).get("get")
    if not pred_url:
        return None

    for _ in range(30):
        getp = requests.get(pred_url, headers=headers, timeout=30)
        if getp.status_code >= 400:
            return None
        pdata = getp.json()
        status = pdata.get("status")
        if status == "succeeded":
            out = pdata.get("output")
            if isinstance(out, list) and out:
                img_url = out[0]
                img_resp = requests.get(img_url, timeout=60)
                if img_resp.status_code >= 400:
                    return None
                return img_resp.content
            return None
        if status in ("failed", "canceled"):
            return None
        time.sleep(2)

    return None


def _fallback_background(size: tuple[int, int]) -> Image.Image:
    w, h = size
    primary = _hex_to_rgb(BRAND_PRIMARY)
    secondary = _hex_to_rgb(BRAND_SECONDARY)
    img = Image.new("RGB", (w, h), primary)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(primary[0] * (1 - t) + secondary[0] * t)
        g = int(primary[1] * (1 - t) + secondary[1] * t)
        b = int(primary[2] * (1 - t) + secondary[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _render_template(background: Image.Image, title: str, cta: str) -> Image.Image:
    img = background.convert("RGB")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    accent = _hex_to_rgb(BRAND_ACCENT)
    card_h = int(h * 0.35)
    draw.rectangle([0, h - card_h, w, h], fill=(255, 255, 255))

    title_font = _load_font(54)
    small_font = _load_font(28)

    x_pad = 60
    y = h - card_h + 40
    max_width = w - (x_pad * 2)

    words = (title or "").split()
    lines: List[str] = []
    cur = ""
    for word in words:
        test = (cur + " " + word).strip()
        tw = draw.textlength(test, font=title_font)
        if tw <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    lines = lines[:3]

    for line in lines:
        draw.text((x_pad, y), line, fill=(15, 23, 42), font=title_font)
        y += 64

    badge_text = cta
    badge_w = int(draw.textlength(badge_text, font=small_font)) + 44
    badge_h = 52
    bx = x_pad
    by = h - 70
    draw.rounded_rectangle([bx, by - badge_h, bx + badge_w, by], radius=14, fill=accent)
    draw.text((bx + 22, by - badge_h + 12), badge_text, fill=(255, 255, 255), font=small_font)

    draw.text((w - x_pad - 220, h - 60), BRAND_NAME, fill=(30, 41, 59), font=small_font)
    return img


def _save_image(img: Image.Image, prefix: str) -> str:
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    name = f"{prefix}_{uuid.uuid4().hex}.png"
    path = Path(UPLOAD_DIR) / name
    img.save(path, format="PNG", optimize=True)
    return name


def _insert_blog_post(payload: Dict[str, Any]) -> int:
    user_id = str(payload.get("user_id") or "").strip()
    url = str(payload.get("url") or "").strip()
    title = str(payload.get("title") or "").strip()
    excerpt = str(payload.get("excerpt") or "").strip()
    hero_image_url = str(payload.get("hero_image_url") or "").strip() or None
    tags = payload.get("tags") or []
    published_at = str(payload.get("published_at") or "").strip() or None

    if not user_id or not url or not title:
        raise HTTPException(status_code=400, detail="user_id, url, title are required")

    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO blog_posts (user_id, url, title, excerpt, hero_image_url, tags, published_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            url,
            title,
            excerpt,
            hero_image_url,
            json.dumps(tags),
            published_at,
            _now_ts(),
        ),
    )
    con.commit()

    cur.execute("SELECT id FROM blog_posts WHERE user_id = ? AND url = ?", (user_id, url))
    row = cur.fetchone()
    con.close()
    if not row:
        raise HTTPException(status_code=500, detail="failed to insert blog post")
    return int(row[0])


def _get_blog_post(blog_post_id: int) -> Dict[str, Any]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT id, user_id, url, title, excerpt, hero_image_url, tags, published_at FROM blog_posts WHERE id = ?",
        (blog_post_id,),
    )
    row = cur.fetchone()
    con.close()
    if not row:
        raise HTTPException(status_code=404, detail="blog post not found")
    return {
        "id": row[0],
        "user_id": row[1],
        "url": row[2],
        "title": row[3],
        "excerpt": row[4] or "",
        "hero_image_url": row[5],
        "tags": json.loads(row[6] or "[]"),
        "published_at": row[7],
    }


def instagram_upload_media(
    access_token: str,
    media_bytes: bytes,
    filename: str,
    media_type: str = 'IMAGE'
) -> Dict[str, Any]:
    """Upload media to Instagram and return media ID."""
    
    # Determine media type based on file extension
    is_video = filename.lower().endswith('.mp4')
    is_carousel = media_type.upper() == 'CAROUSEL'
    
    try:
        # Create media container
        container_url = f"https://graph.facebook.com/v18.0/ig_user_id/media"
        
        container_data = {
            "media_type": f"{media_type.upper()}{'_CHILD' if is_carousel else ''}",
            "upload_type": "RESUMABLE"
        }
        
        if is_video:
            container_data["media_type"] = "REELS"
        
        resp = requests.post(
            container_url,
            params={"access_token": access_token},
            json=container_data,
            timeout=30
        )
        
        if resp.status_code >= 400:
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            raise HTTPException(status_code=400, detail={"platform": "instagram", "error": data})
        
        container_id = resp.json().get("id")
        if not container_id:
            raise HTTPException(status_code=400, detail="Failed to create Instagram media container")
        
        return {"container_id": container_id, "status": "created"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram media upload failed: {str(e)}")


def instagram_publish_media(
    access_token: str,
    container_id: str,
    caption: str = ''
) -> Dict[str, Any]:
    """Publish media container to Instagram."""
    
    try:
        publish_url = f"https://graph.facebook.com/v18.0/ig_user_id/media_publish"
        
        publish_data = {
            "creation_id": container_id,
            "caption": caption,
        }
        
        resp = requests.post(
            publish_url,
            params={"access_token": access_token},
            json=publish_data,
            timeout=30
        )
        
        if resp.status_code >= 400:
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            raise HTTPException(status_code=400, detail={"platform": "instagram", "error": data})
        
        media_id = resp.json().get("id")
        if not media_id:
            raise HTTPException(status_code=400, detail="Failed to publish Instagram media")
        
        # Get permalink
        permalink_url = f"https://graph.facebook.com/v18.0/{media_id}?fields=permalink&access_token={access_token}"
        permalink_resp = requests.get(permalink_url, timeout=30)
        
        permalink = ""
        if permalink_resp.status_code == 200:
            permalink_data = permalink_resp.json()
            permalink = permalink_data.get("permalink", "")
        
        return {
            "id": media_id,
            "permalink": permalink,
            "status": "published"
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram media publish failed: {str(e)}")


def instagram_create_media_carousel(
    access_token: str,
    media_items: List[Dict[str, Any]],
    caption: str = ''
) -> Dict[str, Any]:
    """Create and publish a carousel of media items."""
    
    try:
        # Create carousel container
        container_url = f"https://graph.facebook.com/v18.0/ig_user_id/media"
        
        children_ids = []
        for media_item in media_items:
            # Upload each media item first
            upload_result = instagram_upload_media(
                access_token=access_token,
                media_bytes=media_item["bytes"],
                filename=media_item["filename"],
                media_type="CAROUSEL"
            )
            children_ids.append(upload_result["container_id"])
        
        # Create carousel container
        carousel_data = {
            "media_type": "CAROUSEL",
            "children": children_ids,
            "caption": caption,
        }
        
        resp = requests.post(
            container_url,
            params={"access_token": access_token},
            json=carousel_data,
            timeout=30
        )
        
        if resp.status_code >= 400:
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            raise HTTPException(status_code=400, detail={"platform": "instagram", "error": data})
        
        carousel_id = resp.json().get("id")
        if not carousel_id:
            raise HTTPException(status_code=400, detail="Failed to create Instagram carousel")
        
        # Publish carousel
        publish_result = instagram_publish_media(
            access_token=access_token,
            container_id=carousel_id,
            caption=caption
        )
        
        return publish_result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram carousel creation failed: {str(e)}")


def save_upload_to_disk(
    media_bytes: bytes,
    filename: str
) -> str:
    """Save uploaded media to disk and return filename."""
    
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(filename).suffix
    base_name = Path(filename).stem
    unique_name = f"{base_name}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    file_path = Path(UPLOAD_DIR) / unique_name
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(media_bytes)
    
    return unique_name


def instagram_handle_errors(error_response: str) -> str:
    """Handle Instagram API errors with user-friendly messages."""
    
    error_response = str(error_response).lower()
    
    # Business account errors
    if "the user is not an instagram business" in error_response:
        return "Your Instagram account is not a business account. Please convert it to a business account."
    
    # Token errors
    if "revoked_access_token" in error_response:
        return "Your Instagram access has expired. Please re-authenticate your account."
    
    if "session has been invalidated" in error_response:
        return "Please re-authenticate your Instagram account."
    
    # Media errors
    if "2207003" in error_response:  # Timeout
        return "Timeout downloading media. Please try again."
    
    if "2207020" in error_response:  # Media expired
        return "Media expired. Please upload again."
    
    if "2207032" in error_response:  # Create media failed
        return "Failed to create media. Please try again."
    
    if "2207053" in error_response:  # Invalid thumbnail
        return "Invalid thumbnail offset for video."
    
    if "2207026" in error_response:  # Unsupported video format
        return "Unsupported video format."
    
    if "2207023" in error_response:  # Unknown media type
        return "Unknown media type."
    
    if "2207004" in error_response:  # Image too large
        return "Image is too large. Maximum size is 30MB."
    
    if "2207005" in error_response:  # Unsupported image format
        return "Unsupported image format. Use JPEG or PNG."
    
    if "2207009" in error_response:  # Aspect ratio not supported
        return "Aspect ratio not supported. Must be between 4:5 to 1.91:1."
    
    # Content validation errors
    if "2207028" in error_response:  # Carousel validation failed
        return "Carousel validation failed. Please check your media items."
    
    if "2207010" in error_response:  # Caption too long
        return "Caption is too long. Maximum is 2200 characters."
    
    # Posting limits
    if "page request limit reached" in error_response:
        return "Page posting for today is limited. Please try again tomorrow."
    
    if "2207042" in error_response:  # Daily post limit
        return "You have reached the maximum of 25 posts per day for your account."
    
    # Permission errors
    if "not enough permissions to post" in error_response:
        return "Not enough permissions to post. Please re-authenticate with all permissions."
    
    if "190" in error_response:  # Missing permissions
        return "The account is missing some permissions. Please re-add account and allow all permissions."
    
    # Image resolution errors
    if "36001" in error_response:
        return "Invalid Instagram image resolution. Maximum is 1920x1080px."
    
    # General errors
    if "an unknown error occurred" in error_response:
        return "An unknown error occurred. Please try again later."
    
    if "2207051" in error_response:  # Instagram blocked request
        return "Instagram blocked your request. Please try again later."
    
    if "2207001" in error_response:  # Spam detection
        return "Instagram detected that your post is spam. Please try again with different content."
    
    if "2207027" in error_response:  # Unknown error
        return "Unknown error. Please try again later or contact support."
    
    return "Instagram posting failed. Please try again."


def instagram_get_user_info(access_token: str) -> Dict[str, Any]:
    """Get current Instagram user information."""
    
    try:
        url = "https://graph.facebook.com/v18.0/me"
        params = {
            "fields": "id,username,account_type,media_count,followers_count,follows_count",
            "access_token": access_token
        }
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to get Instagram user info")
        
        data = resp.json()
        
        return {
            "id": data.get("id"),
            "username": data.get("username"),
            "account_type": data.get("account_type"),
            "media_count": data.get("media_count", 0),
            "followers_count": data.get("followers_count", 0),
            "follows_count": data.get("follows_count", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Instagram user info: {str(e)}")


def instagram_get_media_insights(
    access_token: str,
    media_id: str,
    metrics: List[str] = None
) -> Dict[str, Any]:
    """Get insights for a specific media item."""
    
    if not metrics:
        metrics = ["impressions", "reach", "likes", "comments", "shares", "saves"]
    
    try:
        url = f"https://graph.facebook.com/v18.0/{media_id}/insights"
        params = {
            "metric": ",".join(metrics),
            "access_token": access_token
        }
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to get Instagram media insights")
        
        data = resp.json()
        
        return {
            "media_id": media_id,
            "insights": data.get("data", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Instagram insights: {str(e)}")


def linkedin_upload_media(
    access_token: str, 
    author_urn: str, 
    media_bytes: bytes, 
    filename: str
) -> Dict[str, Any]:
    """Upload media (image/video/document) to LinkedIn and return media URN."""
    
    # Determine media type
    is_video = filename.lower().endswith('.mp4')
    is_pdf = filename.lower().endswith('.pdf')
    
    if is_video:
        endpoint = 'videos'
    elif is_pdf:
        endpoint = 'documents'
    else:
        endpoint = 'images'
    
    # Initialize upload
    init_url = f"https://api.linkedin.com/rest/{endpoint}?action=initializeUpload"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202601',
    }
    
    init_body = {
        "initializeUploadRequest": {
            "owner": author_urn,
        }
    }
    
    if is_video:
        init_body["initializeUploadRequest"]["fileSizeBytes"] = len(media_bytes)
        init_body["initializeUploadRequest"]["uploadCaptions"] = False
        init_body["initializeUploadRequest"]["uploadThumbnail"] = False
    
    resp = requests.post(init_url, headers=headers, json=init_body, timeout=30)
    if resp.status_code >= 400:
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        raise HTTPException(status_code=400, detail={"platform": "linkedin", "error": data})
    
    init_data = resp.json()
    upload_url = init_data.get("value", {}).get("uploadUrl")
    media_id = None
    
    if "image" in init_data.get("value", {}):
        media_id = init_data["value"]["image"]
    elif "video" in init_data.get("value", {}):
        media_id = init_data["value"]["video"]
    elif "document" in init_data.get("value", {}):
        media_id = init_data["value"]["document"]
    
    if not upload_url or not media_id:
        raise HTTPException(status_code=400, detail="Failed to initialize LinkedIn media upload")
    
    # Upload the file in chunks
    chunk_size = 1024 * 1024 * 2  # 2MB chunks
    etags = []
    
    for i in range(0, len(media_bytes), chunk_size):
        chunk = media_bytes[i:i + chunk_size]
        
        upload_headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202601',
        }
        
        if is_video:
            upload_headers['Content-Type'] = 'application/octet-stream'
        elif is_pdf:
            upload_headers['Content-Type'] = 'application/pdf'
        
        chunk_resp = requests.put(upload_url, headers=upload_headers, data=chunk, timeout=30)
        if chunk_resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to upload media chunk")
        
        etag = chunk_resp.headers.get('etag')
        if etag:
            etags.append(etag)
    
    # Finalize video upload if needed
    if is_video and etags:
        finalize_url = "https://api.linkedin.com/rest/videos?action=finalizeUpload"
        finalize_body = {
            "finalizeUploadRequest": {
                "video": media_id,
                "uploadToken": "",
                "uploadedPartIds": etags,
            }
        }
        
        finalize_resp = requests.post(finalize_url, headers=headers, json=finalize_body, timeout=30)
        if finalize_resp.status_code >= 400:
            try:
                data = finalize_resp.json()
            except Exception:
                data = {"raw": finalize_resp.text}
            raise HTTPException(status_code=400, detail={"platform": "linkedin", "error": data})
    
    return {"media_urn": media_id, "status": "uploaded"}


def linkedin_fix_text(text: str) -> str:
    """Escape special characters for LinkedIn markdown."""
    import re
    
    # Pattern to match mentions like @[Company Name](urn:li:organization:123)
    pattern = r'@\[.+?\]\(urn:li:organization.+?\)'
    matches = re.findall(pattern, text) or []
    
    # Split text by mentions
    parts = re.split(pattern, text)
    
    # Escape special characters in non-mention parts
    escaped_parts = []
    for part in parts:
        escaped = (
            part.replace('\\', '\\\\')
            .replace('<', '\\<')
            .replace('>', '\\>')
            .replace('#', '\\#')
            .replace('~', '\\~')
            .replace('_', '\\_')
            .replace('|', '\\|')
            .replace('[', '\\[')
            .replace(']', '\\]')
            .replace('*', '\\*')
            .replace('(', '\\(')
            .replace(')', '\\)')
            .replace('{', '\\{')
            .replace('}', '\\}')
            .replace('@', '\\\@')
        )
        escaped_parts.append(escaped)
    
    # Reconstruct text with mentions
    result = []
    for i, part in enumerate(escaped_parts):
        result.append(part)
        if i < len(matches):
            result.append(matches[i])
    
    return ''.join(result)


def linkedin_share_post(author_urn: str, access_token: str, text: str, article_url: Optional[str] = None, media_urns: Optional[List[str]] = None) -> Dict[str, Any]:
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }

    # Determine media content
    content = {}
    
    if media_urns and len(media_urns) > 0:
        if len(media_urns) == 1:
            # Single media
            media_id = media_urns[0]
            if media_id.startswith('urn:li:document'):
                content = {
                    "media": {
                        "title": "Document",
                        "id": media_id,
                    }
                }
            else:
                content = {
                    "media": {
                        "id": media_id,
                    }
                }
        else:
            # Multiple images
            content = {
                "multiImage": {
                    "images": [{"id": urn} for urn in media_urns]
                }
            }
    elif article_url:
        # Article share
        content = {
            "media": [
                {
                    "status": "READY",
                    "originalUrl": article_url,
                }
            ]
        }
    
    # Build post body
    body = {
        "author": author_urn,
        "commentary": linkedin_fix_text(text),
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    
    if content:
        body["content"] = content
    
    # Use the new posts API endpoint
    url = "https://api.linkedin.com/rest/posts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": "202601",
    }

    resp = requests.post(url, headers=headers, json=body, timeout=30)
    if resp.status_code not in (200, 201):
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        raise HTTPException(status_code=400, detail={"platform": "linkedin", "error": data})

    restli_id = resp.headers.get("x-restli-id") or resp.headers.get("X-RestLi-Id")
    return {"restli_id": restli_id, "status_code": resp.status_code, "post_url": f"https://www.linkedin.com/feed/update/{restli_id}" if restli_id else None}


def process_blog_post(blog_post_id: int):
    post = _get_blog_post(blog_post_id)
    captions = _generate_captions_openai(post["title"], post["url"], post["excerpt"], post["tags"])

    base_prompt = f"Professional tech event / blog hero background, abstract gradient, geometric lines, corporate modern, brand palette {BRAND_PRIMARY} {BRAND_SECONDARY} {BRAND_ACCENT}, no text"
    img_bytes = _replicate_sdxl_generate(base_prompt)
    if img_bytes:
        bg = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        bg = bg.resize((1080, 1350))
    else:
        bg = _fallback_background((1080, 1350))

    final = _render_template(bg, post["title"], "Read the blog")
    image_name = _save_image(final, "blog")

    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO content_assets (blog_post_id, captions, prompts, images, created_at) VALUES (?, ?, ?, ?, ?)",
        (
            blog_post_id,
            json.dumps(captions),
            json.dumps({"sdxl_prompt": base_prompt, "provider": SDXL_PROVIDER}),
            json.dumps({"ig_4_5": image_name}),
            _now_ts(),
        ),
    )

    tz = ZoneInfo(DEFAULT_TZ)
    now_dt = datetime.datetime.now(tz=tz)
    for platform in ["instagram", "facebook", "twitter", "linkedin"]:
        peak_dt = _peak_time_for(platform, now_dt)
        if peak_dt <= now_dt:
            peak_dt = peak_dt + datetime.timedelta(days=1)
        scheduled_at = int(peak_dt.timestamp())

        platform_caption = captions.get(platform, {}).get("caption") or f"{post['title']}\n{post['url']}"
        if platform == "twitter":
            hashtags = captions.get(platform, {}).get("hashtags") or []
            if hashtags:
                platform_caption = platform_caption.strip() + "\n\n" + " ".join(hashtags[:4])

        cur.execute(
            """
            INSERT INTO scheduled_posts (blog_post_id, user_id, platform, scheduled_at, status, content, image_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                blog_post_id,
                post["user_id"],
                platform,
                scheduled_at,
                "scheduled",
                platform_caption,
                image_name,
                _now_ts(),
            ),
        )

    con.commit()
    con.close()


def publish_due_scheduled_posts():
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT id, user_id, platform, content, image_path FROM scheduled_posts WHERE status = ? AND scheduled_at <= ? ORDER BY scheduled_at ASC LIMIT 10",
        ("scheduled", _now_ts()),
    )
    rows = cur.fetchall()
    if not rows:
        con.close()
        return

    for row in rows:
        sp_id, user_id, platform, content, image_path = row
        try:
            platform = str(platform).lower().strip()
            if platform == "facebook":
                page_id = os.getenv("FB_PAGE_ID")
                if not page_id:
                    raise Exception("facebook not connected - missing FB_PAGE_ID")
                
                token = get_access_token(user_id, "facebook")
                if not token:
                    raise Exception("facebook not connected")
                
                try:
                    if image_path and Path(UPLOAD_DIR, image_path).exists():
                        # Read image bytes
                        img_bytes = Path(UPLOAD_DIR, image_path).read_bytes()
                        filename = Path(image_path).name
                        
                        # Upload media first
                        media_result = facebook_upload_media(
                            page_id=page_id,
                            page_access_token=token,
                            media_bytes=img_bytes,
                            filename=filename,
                            published=False
                        )
                        
                        # Get media ID
                        media_id = media_result.get("id")
                        if not media_id:
                            raise Exception("Failed to upload media to Facebook")
                        
                        # Create post with media
                        fb_res = facebook_post_with_media(
                            page_id=page_id,
                            page_access_token=token,
                            message=content or "",
                            media_ids=[media_id],
                            published=True
                        )
                    else:
                        # Create text post
                        fb_res = facebook_post_text(page_id, token, content or "")
                    
                    external_id = str(fb_res.get("id") or "")
                    cur.execute(
                        "UPDATE scheduled_posts SET status = ?, external_id = ?, error = NULL WHERE id = ?",
                        ("sent", external_id, sp_id),
                    )
                    
                except Exception as e:
                    error_message = facebook_handle_errors(str(e))
                    cur.execute(
                        "UPDATE scheduled_posts SET status = ?, error = ? WHERE id = ?",
                        ("failed", error_message, sp_id),
                    )

            elif platform == "twitter":
                access_token = get_access_token(user_id, "twitter")
                if not access_token:
                    raise Exception("twitter not connected")

                cur2 = con.cursor()
                cur2.execute(
                    "SELECT meta FROM tokens WHERE user_id = ? AND platform = ?",
                    (user_id, "twitter"),
                )
                mrow = cur2.fetchone()
                meta = json.loads((mrow[0] if mrow else "{}") or "{}")
                access_token_secret = meta.get("access_token_secret")
                api_key = os.getenv("TWITTER_API_KEY") or os.getenv("TWITTER_CONSUMER_KEY")
                api_secret = os.getenv("TWITTER_API_SECRET") or os.getenv("TWITTER_CONSUMER_SECRET")
                if not access_token_secret or not api_key or not api_secret:
                    raise Exception("twitter credentials missing")

                # Handle media upload for scheduled posts
                media_ids = []
                if image_path and Path(UPLOAD_DIR, image_path).exists():
                    try:
                        img_bytes = Path(UPLOAD_DIR, image_path).read_bytes()
                        upload_result = twitter_upload_media(
                            access_token=access_token,
                            access_token_secret=access_token_secret,
                            api_key=api_key,
                            api_secret=api_secret,
                            media_bytes=img_bytes,
                            filename=image_path
                        )
                        media_ids.append(upload_result["media_id"])
                    except Exception as e:
                        raise Exception(f"Failed to upload Twitter media: {str(e)}")
                
                # Create tweet with media
                tweet_result = twitter_post_with_media(
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    api_key=api_key,
                    api_secret=api_secret,
                    content=content or "",
                    media_ids=media_ids if media_ids else None
                )
                
                external_id = str(tweet_result.get("id") or "")
                cur.execute(
                    "UPDATE scheduled_posts SET status = ?, external_id = ?, error = NULL WHERE id = ?",
                    ("sent", external_id, sp_id),
                )

            elif platform == "instagram":
                token = get_access_token(user_id, "instagram")
                if not token:
                    raise Exception("instagram not connected")

                if not image_path or not Path(UPLOAD_DIR, image_path).exists():
                    raise Exception("instagram requires image")

                try:
                    # Read image bytes
                    img_bytes = Path(UPLOAD_DIR, image_path).read_bytes()
                    filename = Path(image_path).name
                    
                    # Upload media to Instagram
                    upload_result = instagram_upload_media(
                        access_token=token,
                        media_bytes=img_bytes,
                        filename=filename,
                        media_type='IMAGE'
                    )
                    
                    # Publish the media
                    publish_result = instagram_publish_media(
                        access_token=token,
                        container_id=upload_result["container_id"],
                        caption=content or ""
                    )
                    
                    external_id = str(publish_result.get("id") or "")
                    cur.execute(
                        "UPDATE scheduled_posts SET status = ?, external_id = ?, error = NULL WHERE id = ?",
                        ("sent", external_id, sp_id),
                    )
                    
                except Exception as e:
                    error_message = instagram_handle_errors(str(e))
                    cur.execute(
                        "UPDATE scheduled_posts SET status = ?, error = ? WHERE id = ?",
                        ("failed", error_message, sp_id),
                    )

            elif platform == "linkedin":
                token = get_access_token(user_id, "linkedin")
                if not token:
                    raise Exception("linkedin not connected")
                if not LINKEDIN_AUTHOR_URN:
                    raise Exception("missing LINKEDIN_AUTHOR_URN")

                blog_url = None
                try:
                    cur3 = con.cursor()
                    cur3.execute("SELECT blog_post_id FROM scheduled_posts WHERE id = ?", (sp_id,))
                    brow = cur3.fetchone()
                    if brow:
                        bp = _get_blog_post(int(brow[0]))
                        blog_url = bp.get("url")
                except Exception:
                    blog_url = None

                # Handle media upload for scheduled posts
                media_urns = []
                if image_path and Path(UPLOAD_DIR, image_path).exists():
                    try:
                        img_bytes = Path(UPLOAD_DIR, image_path).read_bytes()
                        upload_result = linkedin_upload_media(
                            access_token=token,
                            author_urn=LINKEDIN_AUTHOR_URN,
                            media_bytes=img_bytes,
                            filename=image_path
                        )
                        media_urns.append(upload_result["media_urn"])
                    except Exception as e:
                        raise Exception(f"Failed to upload LinkedIn media: {str(e)}")

                res = linkedin_share_post(
                    author_urn=LINKEDIN_AUTHOR_URN,
                    access_token=token,
                    text=content or "",
                    article_url=blog_url,
                    media_urns=media_urns if media_urns else None
                )

                external_id = res.get("restli_id") or ""
                cur.execute(
                    "UPDATE scheduled_posts SET status = ?, external_id = ?, error = NULL WHERE id = ?",
                    ("sent", str(external_id), sp_id),
                )
            else:
                cur.execute(
                    "UPDATE scheduled_posts SET status = ?, error = ? WHERE id = ?",
                    ("failed", "unsupported platform", sp_id),
                )

        except Exception as e:
            cur.execute(
                "UPDATE scheduled_posts SET status = ?, error = ? WHERE id = ?",
                ("failed", str(e), sp_id),
            )

    con.commit()
    con.close()


def get_access_token(user_id: str, platform: str) -> Optional[str]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT access_token FROM tokens WHERE user_id = ? AND platform = ?",
        (user_id, platform),
    )
    row = cur.fetchone()
    con.close()
    return row[0] if row else None


def get_connected_platforms(user_id: str) -> List[str]:
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT platform FROM tokens WHERE user_id = ?",
        (user_id,),
    )
    rows = cur.fetchall()
    con.close()
    return [r[0] for r in rows]


def twitter_upload_media(
    access_token: str,
    access_token_secret: str,
    api_key: str,
    api_secret: str,
    media_bytes: bytes,
    filename: str
) -> Dict[str, Any]:
    """Upload media to Twitter/X and return media ID."""
    
    tweepy = _tweepy()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    
    # Determine media type
    is_video = filename.lower().endswith('.mp4')
    is_gif = filename.lower().endswith('.gif')
    
    try:
        if is_video:
            # Upload video
            media = api.media_upload(
                filename=filename,
                file=io.BytesIO(media_bytes),
                media_category='tweet_video'
            )
        elif is_gif:
            # Upload GIF (as animated GIF)
            media = api.media_upload(
                filename=filename,
                file=io.BytesIO(media_bytes),
                media_category='tweet_gif'
            )
        else:
            # Upload image (resize if needed)
            try:
                # Resize image to optimize for Twitter
                img = Image.open(io.BytesIO(media_bytes))
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize to max 1000px width while maintaining aspect ratio
                if img.width > 1000:
                    ratio = 1000 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1000, new_height), Image.Resampling.LANCZOS)
                
                # Convert to bytes
                img_bytes_resized = io.BytesIO()
                img.save(img_bytes_resized, format='JPEG', quality=85, optimize=True)
                img_bytes_resized.seek(0)
                
                media = api.media_upload(
                    filename=filename.replace('.png', '.jpg'),
                    file=img_bytes_resized,
                    media_category='tweet_image'
                )
            except Exception:
                # Fallback to original bytes
                media = api.media_upload(
                    filename=filename,
                    file=io.BytesIO(media_bytes),
                    media_category='tweet_image'
                )
        
        return {"media_id": media.media_id_string, "status": "uploaded"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to upload media to Twitter: {str(e)}")


def twitter_post_with_media(
    access_token: str,
    access_token_secret: str,
    api_key: str,
    api_secret: str,
    content: str,
    media_ids: List[str] = None,
    reply_to_tweet_id: str = None,
    who_can_reply: str = None
) -> Dict[str, Any]:
    """Post to Twitter/X with media and advanced options."""
    
    tweepy = _tweepy()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    
    try:
        # Prepare tweet parameters
        tweet_params = {
            'status': content
        }
        
        # Add media if present
        if media_ids:
            tweet_params['media_ids'] = media_ids
        
        # Add reply if specified
        if reply_to_tweet_id:
            tweet_params['in_reply_to_status_id'] = reply_to_tweet_id
            tweet_params['auto_populate_reply_metadata'] = True
        
        # Add reply restrictions if specified
        if who_can_reply and who_can_reply != 'everyone':
            # Twitter API v1.1 doesn't support reply restrictions directly
            # This would need API v2 for full functionality
            pass
        
        # Post tweet
        tweet = api.update_status(**tweet_params)
        
        return {
            "id": tweet.id,
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
            "user": {
                "screen_name": tweet.user.screen_name if tweet.user else None,
                "name": tweet.user.name if tweet.user else None
            },
            "entities": tweet._json.get('entities', {}),
            "public_metrics": tweet._json.get('public_metrics', {})
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Handle specific Twitter errors
        if "duplicate" in error_msg.lower():
            raise HTTPException(status_code=400, detail="You have already posted this content. Please wait before posting again.")
        elif "usage-capped" in error_msg.lower():
            raise HTTPException(status_code=400, detail="Twitter posting limit reached. Please try again later.")
        elif "invalid URL" in error_msg:
            raise HTTPException(status_code=400, detail="The tweet contains a URL that is not allowed on X.")
        elif "video longer than" in error_msg.lower():
            raise HTTPException(status_code=400, detail="The video is longer than the allowed duration for this account.")
        else:
            raise HTTPException(status_code=400, detail=f"Twitter posting failed: {error_msg}")


def twitter_get_user_info(access_token: str, access_token_secret: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Get current user information from Twitter/X."""
    
    tweepy = _tweepy()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    
    try:
        user = api.verify_credentials(include_entities=False, skip_status=True, include_email=True)
        return {
            "id": user.id_str,
            "username": user.screen_name,
            "name": user.name,
            "verified": user.verified,
            "profile_image_url": user.profile_image_url_https,
            "protected": user.protected,
            "followers_count": user.followers_count,
            "following_count": user.friends_count,
            "tweet_count": user.statuses_count
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Twitter user info: {str(e)}")


def twitter_get_tweet_metrics(access_token: str, access_token_secret: str, api_key: str, api_secret: str, tweet_id: str) -> Dict[str, Any]:
    """Get detailed metrics for a specific tweet."""
    
    tweepy = _tweepy()
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    
    try:
        tweet = api.get_status(tweet_id, include_entities=True, tweet_mode='extended')
        
        return {
            "id": tweet.id_str,
            "text": tweet.full_text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
            "public_metrics": {
                "retweet_count": tweet.retweet_count,
                "like_count": tweet.favorite_count,
                "reply_count": tweet.reply_count if hasattr(tweet, 'reply_count') else 0,
                "quote_count": tweet.quote_count if hasattr(tweet, 'quote_count') else 0
            },
            "entities": tweet.entities if hasattr(tweet, 'entities') else {}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get tweet metrics: {str(e)}")


def _tweepy():
    try:
        import tweepy  # type: ignore

        return tweepy
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Twitter integration not available in this Python environment: {e}",
        )


@app.get("/auth/status")
def auth_status(user_id: str):
    platforms = get_connected_platforms(user_id)
    return {
        "user_id": user_id,
        "connected": {
            "facebook": "facebook" in platforms,
            "instagram": "instagram" in platforms,
            "twitter": "twitter" in platforms,
            "linkedin": "linkedin" in platforms,
        },
    }


def upsert_access_token(user_id: str, platform: str, access_token: str, meta: Optional[dict] = None):
    con = db_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO tokens (user_id, platform, access_token, meta)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, platform)
        DO UPDATE SET access_token=excluded.access_token, meta=excluded.meta
        """,
        (user_id, platform, access_token, json.dumps(meta or {})),
    )
    con.commit()
    con.close()


def facebook_upload_media(
    page_id: str,
    page_access_token: str,
    media_bytes: bytes,
    filename: str,
    published: bool = False
) -> Dict[str, Any]:
    """Upload media to Facebook and return media ID."""
    
    try:
        # Determine media type
        is_video = filename.lower().endswith('.mp4')
        
        if is_video:
            # Upload video
            url = f"{META_GRAPH_BASE}/{page_id}/videos"
            data = {
                "description": "",
                "published": str(published).lower(),
            }
            files = {"source": (filename, media_bytes, "video/mp4")}
        else:
            # Upload image
            url = f"{META_GRAPH_BASE}/{page_id}/photos"
            data = {
                "published": str(published).lower(),
            }
            files = {"source": (filename, media_bytes, "image/jpeg")}
        
        data["access_token"] = page_access_token
        
        resp = requests.post(url, data=data, files=files, timeout=120)
        
        if resp.status_code >= 400:
            try:
                error_data = resp.json()
            except Exception:
                error_data = {"raw": resp.text}
            raise HTTPException(status_code=400, detail={"platform": "facebook", "error": error_data})
        
        return resp.json()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Facebook media upload failed: {str(e)}")


def facebook_post_with_media(
    page_id: str,
    page_access_token: str,
    message: str,
    media_ids: List[str] = None,
    link: str = None,
    published: bool = True
) -> Dict[str, Any]:
    """Post to Facebook with media and advanced options."""
    
    try:
        url = f"{META_GRAPH_BASE}/{page_id}/feed"
        
        post_data = {
            "message": message,
            "published": str(published).lower(),
            "access_token": page_access_token,
        }
        
        # Add media if present
        if media_ids:
            post_data["attached_media"] = [
                {"media_fbid": media_id} for media_id in media_ids
            ]
        
        # Add link if specified
        if link:
            post_data["link"] = link
        
        resp = requests.post(url, data=post_data, timeout=30)
        
        if resp.status_code >= 400:
            try:
                error_data = resp.json()
            except Exception:
                error_data = {"raw": resp.text}
            raise HTTPException(status_code=400, detail={"platform": "facebook", "error": error_data})
        
        return resp.json()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Facebook posting failed: {str(e)}")


def facebook_post_video(
    page_id: str,
    page_access_token: str,
    video_bytes: bytes,
    filename: str,
    description: str = "",
    published: bool = True
) -> Dict[str, Any]:
    """Post video to Facebook."""
    
    try:
        url = f"{META_GRAPH_BASE}/{page_id}/videos"
        
        data = {
            "description": description,
            "published": str(published).lower(),
            "access_token": page_access_token,
        }
        
        files = {"source": (filename, video_bytes, "video/mp4")}
        
        resp = requests.post(url, data=data, files=files, timeout=300)
        
        if resp.status_code >= 400:
            try:
                error_data = resp.json()
            except Exception:
                error_data = {"raw": resp.text}
            raise HTTPException(status_code=400, detail={"platform": "facebook", "error": error_data})
        
        return resp.json()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Facebook video posting failed: {str(e)}")


def facebook_handle_errors(error_response: str) -> str:
    """Handle Facebook API errors with user-friendly messages."""
    
    error_response = str(error_response).lower()
    
    # Access token errors
    if "error validating access token" in error_response:
        return "Please re-authenticate your Facebook account."
    
    if "490" in error_response:
        return "Access token expired, please re-authenticate."
    
    if "revoked_access_token" in error_response:
        return "Access token has been revoked, please re-authenticate."
    
    # Media errors
    if "1366046" in error_response:
        return "Photos should be smaller than 4 MB and saved as JPG, PNG."
    
    # Rate limiting
    if "1390008" in error_response:
        return "You are posting too fast, please slow down."
    
    # Content policy violations
    if "1346003" in error_response:
        return "Content flagged as abusive by Facebook."
    
    if "1404006" in error_response:
        return "Security check required by Facebook. Please try again later."
    
    if "1404102" in error_response:
        return "Content violates Facebook Community Standards."
    
    # Permission errors
    if "1404078" in error_response:
        return "Page publishing authorization required, please re-authenticate."
    
    if "1609008" in error_response:
        return "Cannot post Facebook.com links."
    
    # URL validation
    if "2061006" in error_response:
        return "Invalid URL format in post content."
    
    # Content validation
    if "1349125" in error_response:
        return "Invalid content format."
    
    if "1404112" in error_response:
        return "Account temporarily limited for security reasons. Please try again later."
    
    if "name parameter too long" in error_response:
        return "Post content is too long. Maximum is 63,206 characters."
    
    # Service errors
    if "1363047" in error_response or "1609010" in error_response:
        return "Facebook service temporarily unavailable. Please try again later."
    
    return "Facebook posting failed. Please try again."


def facebook_get_page_info(
    page_id: str,
    page_access_token: str
) -> Dict[str, Any]:
    """Get Facebook page information."""
    
    try:
        url = f"{META_GRAPH_BASE}/{page_id}"
        params = {
            "fields": "id,name,username,fan_count,talking_about_count,picture.type(large),cover",
            "access_token": page_access_token
        }
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to get Facebook page info")
        
        data = resp.json()
        
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "username": data.get("username"),
            "fan_count": data.get("fan_count", 0),
            "talking_about_count": data.get("talking_about_count", 0),
            "picture": data.get("picture", {}).get("data", {}).get("url", ""),
            "cover": data.get("cover", {}).get("source", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Facebook page info: {str(e)}")


def facebook_get_page_insights(
    page_id: str,
    page_access_token: str,
    metrics: List[str] = None,
    period: str = "day",
    days: int = 7
) -> Dict[str, Any]:
    """Get Facebook page insights."""
    
    if not metrics:
        metrics = [
            "page_impressions_unique",
            "page_post_engagements",
            "page_posts_impressions_unique",
            "page_daily_follows",
            "page_video_views"
        ]
    
    try:
        url = f"{META_GRAPH_BASE}/{page_id}/insights"
        params = {
            "metric": ",".join(metrics),
            "period": period,
            "since": dayjs().subtract(days, 'day').unix(),
            "until": dayjs().unix(),
            "access_token": page_access_token
        }
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to get Facebook page insights")
        
        data = resp.json()
        
        return {
            "page_id": page_id,
            "insights": data.get("data", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Facebook insights: {str(e)}")


def facebook_get_post_insights(
    post_id: str,
    page_access_token: str,
    metrics: List[str] = None
) -> Dict[str, Any]:
    """Get insights for a specific Facebook post."""
    
    if not metrics:
        metrics = [
            "post_impressions_unique",
            "post_reactions_by_type_total",
            "post_clicks",
            "post_clicks_by_type"
        ]
    
    try:
        url = f"{META_GRAPH_BASE}/{post_id}/insights"
        params = {
            "metric": ",".join(metrics),
            "access_token": page_access_token
        }
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to get Facebook post insights")
        
        data = resp.json()
        
        return {
            "post_id": post_id,
            "insights": data.get("data", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Facebook post insights: {str(e)}")


def facebook_get_user_pages(
    user_access_token: str
) -> List[Dict[str, Any]]:
    """Get all Facebook pages for the user."""
    
    try:
        url = f"{META_GRAPH_BASE}/me/accounts"
        params = {
            "fields": "id,name,username,picture.type(large),access_token",
            "access_token": user_access_token
        }
        
        resp = requests.get(url, params=params, timeout=30)
        
        if resp.status_code >= 400:
            raise HTTPException(status_code=400, detail="Failed to get Facebook pages")
        
        data = resp.json()
        
        return data.get("data", [])
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get Facebook pages: {str(e)}")


def facebook_post_text(page_id: str, page_access_token: str, message: str) -> Dict[str, Any]:
    url = f"{META_GRAPH_BASE}/{page_id}/feed"
    resp = requests.post(
        url,
        data={
            "message": message,
            "access_token": page_access_token,
        },
        timeout=30,
    )
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail={"platform": "facebook", "error": data})
    return data


def facebook_post_photo(
    page_id: str,
    page_access_token: str,
    message: str,
    image_bytes: bytes,
    filename: str,
) -> Dict[str, Any]:
    url = f"{META_GRAPH_BASE}/{page_id}/photos"
    files = {"source": (filename, image_bytes, "application/octet-stream")}
    data = {"caption": message, "access_token": page_access_token}

    resp = requests.post(url, data=data, files=files, timeout=60)
    try:
        out = resp.json()
    except Exception:
        out = {"raw": resp.text}

    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail={"platform": "facebook", "error": out})
    return out


@app.post("/post/send")
async def send_post(
    user_id: str = Form(...),
    content: str = Form(...),
    platforms: str = Form(...),
    image: Optional[UploadFile] = File(None),
):
    try:
        platforms_list: List[str] = json.loads(platforms)
        if not isinstance(platforms_list, list):
            raise ValueError
    except Exception:
        raise HTTPException(status_code=400, detail="`platforms` must be a JSON array string.")

    image_bytes = await image.read() if image else None
    image_name = image.filename if image else None

    results = []
    for p in platforms_list:
        p = str(p).lower().strip()
        try:
            if p == "facebook":
                page_id = os.getenv("FB_PAGE_ID")
                if not page_id:
                    raise HTTPException(status_code=400, detail="Missing FB_PAGE_ID in environment.")

                token = get_access_token(user_id, "facebook")
                if not token:
                    raise HTTPException(status_code=401, detail="Facebook not connected for this user.")

                try:
                    if image_bytes:
                        # Upload media first
                        media_result = facebook_upload_media(
                            page_id=page_id,
                            page_access_token=token,
                            media_bytes=image_bytes,
                            filename=image_name or "upload",
                            published=False
                        )
                        
                        # Get media ID
                        media_id = media_result.get("id")
                        if not media_id:
                            raise HTTPException(status_code=400, detail="Failed to upload media to Facebook")
                        
                        # Create post with media
                        fb_res = facebook_post_with_media(
                            page_id=page_id,
                            page_access_token=token,
                            message=content,
                            media_ids=[media_id],
                            published=True
                        )
                    else:
                        # Create text post
                        fb_res = facebook_post_text(page_id, token, content)
                    
                    results.append({
                        "platform": "facebook", 
                        "status": "success", 
                        "response": {
                            "id": fb_res.get("id"),
                            "permalink_url": fb_res.get("permalink_url")
                        }
                    })
                    
                except Exception as e:
                    # Handle Facebook errors with user-friendly messages
                    error_message = facebook_handle_errors(str(e))
                    raise HTTPException(status_code=400, detail=error_message)

            elif p == "twitter":
                access_token = get_access_token(user_id, "twitter")
                if not access_token:
                    raise HTTPException(status_code=401, detail="Twitter not connected for this user.")

                con = db_conn()
                cur = con.cursor()
                cur.execute(
                    "SELECT meta FROM tokens WHERE user_id = ? AND platform = ?",
                    (user_id, "twitter"),
                )
                row = cur.fetchone()
                con.close()
                meta = json.loads((row[0] if row else "{}") or "{}")
                access_token_secret = meta.get("access_token_secret")
                if not access_token_secret:
                    raise HTTPException(status_code=400, detail="Missing twitter access_token_secret")

                api_key = os.getenv("TWITTER_API_KEY") or os.getenv("TWITTER_CONSUMER_KEY")
                api_secret = os.getenv("TWITTER_API_SECRET") or os.getenv("TWITTER_CONSUMER_SECRET")
                if not api_key or not api_secret:
                    raise HTTPException(status_code=400, detail="Missing TWITTER_API_KEY/TWITTER_API_SECRET")

                # Handle media upload if present
                media_ids = []
                if image_bytes:
                    try:
                        upload_result = twitter_upload_media(
                            access_token=access_token,
                            access_token_secret=access_token_secret,
                            api_key=api_key,
                            api_secret=api_secret,
                            media_bytes=image_bytes,
                            filename=image_name or "upload"
                        )
                        media_ids.append(upload_result["media_id"])
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"Failed to upload media to Twitter: {str(e)}")
                
                # Create tweet with media
                tweet_result = twitter_post_with_media(
                    access_token=access_token,
                    access_token_secret=access_token_secret,
                    api_key=api_key,
                    api_secret=api_secret,
                    content=content,
                    media_ids=media_ids if media_ids else None
                )
                
                results.append({
                    "platform": "twitter", 
                    "status": "success", 
                    "response": {
                        "id": tweet_result.get("id"),
                        "text": tweet_result.get("text"),
                        "url": f"https://twitter.com/{tweet_result.get('user', {}).get('screen_name')}/status/{tweet_result.get('id')}"
                    }
                })

            elif p == "instagram":
                ig_user_id = os.getenv("IG_USER_ID")
                if not ig_user_id:
                    raise HTTPException(status_code=400, detail="Missing IG_USER_ID in environment.")

                token = get_access_token(user_id, "instagram")
                if not token:
                    raise HTTPException(status_code=401, detail="Instagram not connected for this user.")

                if not image_bytes:
                    raise HTTPException(status_code=400, detail="Instagram requires at least one attachment.")

                try:
                    # Save image to disk
                    filename = save_upload_to_disk(image_bytes, image_name or "upload")
                    
                    # Upload media to Instagram
                    upload_result = instagram_upload_media(
                        access_token=token,
                        media_bytes=image_bytes,
                        filename=filename,
                        media_type='IMAGE'
                    )
                    
                    # Publish the media
                    publish_result = instagram_publish_media(
                        access_token=token,
                        container_id=upload_result["container_id"],
                        caption=content
                    )
                    
                    results.append({
                        "platform": "instagram", 
                        "status": "success", 
                        "response": {
                            "id": publish_result.get("id"),
                            "permalink": publish_result.get("permalink"),
                            "url": publish_result.get("permalink")
                        }
                    })
                    
                except Exception as e:
                    # Handle Instagram errors with user-friendly messages
                    error_message = instagram_handle_errors(str(e))
                    raise HTTPException(status_code=400, detail=error_message)

            elif p == "linkedin":
                token = get_access_token(user_id, "linkedin")
                if not token:
                    raise HTTPException(status_code=401, detail="LinkedIn not connected for this user.")
                
                author_urn = os.getenv("LINKEDIN_AUTHOR_URN")
                if not author_urn:
                    raise HTTPException(status_code=400, detail="Missing LINKEDIN_AUTHOR_URN in environment.")
                
                # Handle media upload if present
                media_urns = []
                if image_bytes:
                    try:
                        # Upload media to LinkedIn
                        upload_result = linkedin_upload_media(
                            access_token=token,
                            author_urn=author_urn,
                            media_bytes=image_bytes,
                            filename=image_name or "upload"
                        )
                        media_urns.append(upload_result["media_urn"])
                    except Exception as e:
                        raise HTTPException(status_code=400, detail=f"Failed to upload media to LinkedIn: {str(e)}")
                
                # Create the post
                li_res = linkedin_share_post(
                    author_urn=author_urn,
                    access_token=token,
                    text=content,
                    article_url=None,
                    media_urns=media_urns if media_urns else None
                )
                
                results.append({
                    "platform": "linkedin", 
                    "status": "success", 
                    "response": {
                        "id": li_res.get("restli_id"),
                        "post_url": li_res.get("post_url")
                    }
                })

            else:
                results.append({"platform": p, "status": "failed", "error": "Unknown platform"})

        except HTTPException as e:
            results.append({"platform": p, "status": "failed", "error": e.detail})
        except Exception as e:
            results.append({"platform": p, "status": "failed", "error": str(e)})

    return {"request_id": str(uuid.uuid4()), "results": results}


@app.get("/auth/connect")
def auth_connect(platform: str, user_id: str):
    platform = platform.lower().strip()

    if platform in ("facebook", "instagram"):
        app_id, _, redirect_uri = get_meta_oauth_config()
        scopes = [
            "public_profile",
            "pages_show_list",
            "pages_read_engagement",
            "pages_manage_posts",
            "instagram_basic",
            "instagram_content_publish",
        ]
        state = create_oauth_state(user_id=user_id, platform=platform)
        params = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
            "scope": ",".join(scopes),
        }
        url = "https://www.facebook.com/v19.0/dialog/oauth?" + urllib.parse.urlencode(params)
        return {"authorize_url": url}

    if platform == "twitter":
        api_key = os.getenv("TWITTER_API_KEY") or os.getenv("TWITTER_CONSUMER_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET") or os.getenv("TWITTER_CONSUMER_SECRET")
        redirect_uri = os.getenv("TWITTER_REDIRECT_URI")
        if not api_key or not api_secret or not redirect_uri:
            raise HTTPException(status_code=400, detail="Missing TWITTER_API_KEY/TWITTER_API_SECRET/TWITTER_REDIRECT_URI")

        state = create_oauth_state(user_id=user_id, platform="twitter")
        callback_with_state = redirect_uri + ("&" if "?" in redirect_uri else "?") + "state=" + urllib.parse.quote(state)

        tweepy = _tweepy()
        oauth = tweepy.OAuth1UserHandler(api_key, api_secret, callback=callback_with_state)
        auth_url = oauth.get_authorization_url(signin_with_twitter=True)

        con = db_conn()
        cur = con.cursor()
        cur.execute(
            "UPDATE oauth_states SET meta = ? WHERE state = ?",
            (
                json.dumps(
                    {
                        "request_token": oauth.request_token.get("oauth_token"),
                        "request_token_secret": oauth.request_token.get("oauth_token_secret"),
                    }
                ),
                state,
            ),
        )
        con.commit()
        con.close()

        return {"authorize_url": auth_url}

    if platform == "linkedin":
        client_id = os.getenv("LINKEDIN_CLIENT_ID")
        redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
        if not client_id or not redirect_uri:
            raise HTTPException(status_code=400, detail="Missing LINKEDIN_CLIENT_ID/LINKEDIN_REDIRECT_URI")
        scopes = ["openid", "profile", "email", "w_member_social"]
        state = create_oauth_state(user_id=user_id, platform=platform)
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": " ".join(scopes),
        }
        url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)
        return {"authorize_url": url}

    raise HTTPException(status_code=400, detail="Unsupported platform")


@app.get("/auth/callback")
def auth_callback(
    platform: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    oauth_verifier: Optional[str] = None,
):
    platform = platform.lower().strip()
    if not state:
        raise HTTPException(status_code=400, detail="Missing state")

    payload = consume_oauth_state(state=state, platform=platform)
    user_id = payload["user_id"]
    meta = payload.get("meta") or {}

    if platform in ("facebook", "instagram"):
        if not code:
            raise HTTPException(status_code=400, detail="Missing code")

        user_access_token = exchange_meta_code_for_token(code)

        if platform == "facebook":
            page_id = os.getenv("FB_PAGE_ID")
            if not page_id:
                raise HTTPException(status_code=400, detail="Missing FB_PAGE_ID")

            page_token = get_facebook_page_access_token(user_access_token=user_access_token, page_id=page_id)
            upsert_access_token(user_id=user_id, platform="facebook", access_token=page_token, meta={"page_id": page_id})
            return {"status": "connected", "platform": "facebook"}

        if platform == "instagram":
            upsert_access_token(user_id=user_id, platform="instagram", access_token=user_access_token, meta={})
            return {"status": "connected", "platform": "instagram"}

        if platform == "linkedin":
            client_id = os.getenv("LINKEDIN_CLIENT_ID")
            client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
            redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
            if not client_id or not client_secret or not redirect_uri:
                raise HTTPException(status_code=400, detail="Missing LINKEDIN_CLIENT_ID/LINKEDIN_CLIENT_SECRET/LINKEDIN_REDIRECT_URI")
            token_url = "https://www.linkedin.com/oauth/v2/accessToken"
            resp = requests.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                },
                timeout=30,
            )
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            if resp.status_code >= 400:
                raise HTTPException(status_code=400, detail={"platform": "linkedin", "error": data})
            token = data.get("access_token")
            if not token:
                raise HTTPException(status_code=400, detail={"platform": "linkedin", "error": "Missing access_token in response"})
            upsert_access_token(user_id=user_id, platform="linkedin", access_token=token, meta={})
            return {"status": "connected", "platform": "linkedin"}

        if platform == "twitter":
            api_key = os.getenv("TWITTER_API_KEY") or os.getenv("TWITTER_CONSUMER_KEY")
            api_secret = os.getenv("TWITTER_API_SECRET") or os.getenv("TWITTER_CONSUMER_SECRET")
            if not api_key or not api_secret:
                raise HTTPException(status_code=400, detail="Missing TWITTER_API_KEY/TWITTER_API_SECRET")

            if not oauth_verifier:
                raise HTTPException(status_code=400, detail="Missing oauth_verifier")

            req_token = meta.get("request_token")
            req_secret = meta.get("request_token_secret")
            if not req_token or not req_secret:
                raise HTTPException(status_code=400, detail="Missing request token in state")

            tweepy = _tweepy()
            oauth = tweepy.OAuth1UserHandler(api_key, api_secret)
            oauth.request_token = {"oauth_token": req_token, "oauth_token_secret": req_secret}
            access_token, access_token_secret = oauth.get_access_token(oauth_verifier)

            upsert_access_token(
                user_id=user_id,
                platform="twitter",
                access_token=access_token,
                meta={"access_token_secret": access_token_secret},
            )
            return {"status": "connected", "platform": "twitter"}

    raise HTTPException(status_code=400, detail="Unsupported platform")


@app.post("/tokens/save")
def dev_save_token(
    user_id: str = Form(...),
    platform: str = Form(...),
    access_token: str = Form(...),
    meta: Optional[str] = Form(None),
    dev_token: Optional[str] = Form(None),
):
    if DEV_TOKEN:
        if not dev_token or dev_token != DEV_TOKEN:
            raise HTTPException(status_code=403, detail="Forbidden")

    try:
        meta_obj = json.loads(meta) if meta else {}
    except Exception:
        raise HTTPException(status_code=400, detail="meta must be valid JSON")

    upsert_access_token(user_id=user_id, platform=platform.lower().strip(), access_token=access_token, meta=meta_obj)
    return {"status": "saved"}
