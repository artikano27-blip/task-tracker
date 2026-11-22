import html
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

TEMPLATES_DIR = Path(__file__).resolve().parent

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def format_summary_to_html(summary_text: str) -> str:
    safe_text = html.escape(summary_text.strip())
    safe_text = re.sub(
        r"\*\*(.+?)\*\*",
        r'<strong style="color: #172B4D; font-weight: 600;">\1</strong>',
        safe_text,
    )
    paragraphs = [p.strip() for p in safe_text.split("\n\n") if p.strip()]
    return "\n".join(
        f'<p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #172B4D;">{p.replace(chr(10), "<br>")}</p>'
        for p in paragraphs
    )


def render_daily_summary(username: str, summary_text: str) -> str:
    template = env.get_template("daily_summary.html")
    return template.render(
        username=username,  # Jinja2 сама экранирует username благодаря autoescape
        formatted_content=format_summary_to_html(summary_text),
        app_url=settings.FRONTEND_URL,
    )

def render_welcome_email(username: str) -> str:
    template = env.get_template("registration.html")
    return template.render(
        username=username,
        app_url=settings.FRONTEND_URL,
    )