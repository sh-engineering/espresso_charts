# ============================================================================
# ESPRESSO CHARTS — GITHUB UPLOADER + SUBSTACK PUBLISHER
# ============================================================================
# Add to your espresso_charts_main.ipynb as a new section.
# No UI. Call functions directly from notebook cells.
#
# SETUP (run once per session):
#   uploader = GitHubUploader(token="ghp_xxx", owner="you", repo="espresso-charts")
#   substack = SubstackPublisher(publication_url="https://yourpub.substack.com",
#                                 email="you@email.com", password="yourpassword")
#
# GITHUB USAGE:
#   uploader.push_file("/content/chart.png", dest="assets/2026-02-buffett.png")
#   uploader.push_figure(fig, dest="assets/2026-02-buffett.png")
#   uploader.push_text(caption_text, dest="prompts/04_instagram_caption.md")
#   uploader.push_story_pack("02-buffett-indicator", {...})
#
# SUBSTACK USAGE:
#   substack.post_draft(title="...", body="...", subtitle="...")
#   substack.post_scheduled(title="...", body="...", publish_at="2026-02-25T08:00:00")
#   substack.post_now(title="...", body="...", subtitle="...")
# ============================================================================

import requests
import base64
import json
import io
import os
from pathlib import Path
from datetime import datetime


# ============================================================================
# GITHUB UPLOADER
# ============================================================================

class GitHubUploader:
    """Push files, figures, and text to your GitHub repo from Colab."""

    def __init__(self, token: str, owner: str, repo: str, branch: str = "main"):
        self.token  = token
        self.owner  = owner
        self.repo   = repo
        self.branch = branch

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        }

    def _get_sha(self, path: str):
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        r   = requests.get(url, headers=self._headers())
        return r.json().get("sha") if r.ok else None

    def _push(self, path: str, content_b64: str, commit_msg: str):
        url  = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        body = {"message": commit_msg, "content": content_b64, "branch": self.branch}
        sha  = self._get_sha(path)
        if sha:
            body["sha"] = sha
        r = requests.put(url, headers=self._headers(), data=json.dumps(body))
        if not r.ok:
            raise RuntimeError(f"GitHub {r.status_code}: {r.json().get('message')}")
        return r.json()

    # ── Public methods ────────────────────────────────────────────────────────

    def push_file(self, local_path: str, dest: str = None, commit_msg: str = None):
        """
        Push a local file to GitHub.

        Args:
            local_path:  Path on disk, e.g. "/content/chart.png"
            dest:        Repo path, e.g. "assets/2026-02-buffett.png"
                         Defaults to assets/<filename>
            commit_msg:  Defaults to "Upload <filename> [YYYY-MM-DD]"

        Example:
            uploader.push_file("/content/chart_sq.png", dest="assets/2026-02-buffett-sq.png")
        """
        local_path = Path(local_path)
        dest       = dest or f"assets/{local_path.name}"
        msg        = commit_msg or f"Upload {local_path.name} [{datetime.now().strftime('%Y-%m-%d')}]"

        with open(local_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        self._push(dest, b64, msg)
        print(f"✅  {local_path.name}  →  {dest}")

    def push_figure(self, fig, dest: str, dpi: int = 200, commit_msg: str = None):
        """
        Push a matplotlib Figure directly — no saving to disk needed.

        Args:
            fig:   Matplotlib Figure object
            dest:  Repo path, e.g. "assets/2026-02-buffett.png"
            dpi:   Resolution (default 200, matches your chart pipeline)

        Example:
            uploader.push_figure(fig, dest="assets/2026-02-buffett-sq.png")
        """
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        buf.seek(0)
        b64  = base64.b64encode(buf.read()).decode()
        name = Path(dest).name
        msg  = commit_msg or f"Push chart {name} [{datetime.now().strftime('%Y-%m-%d')}]"

        self._push(dest, b64, msg)
        print(f"✅  {name}  →  {dest}")

    def push_text(self, text: str, dest: str, commit_msg: str = None):
        """
        Push a string (prompt, caption, article, markdown) to GitHub.

        Args:
            text:  The text content to save
            dest:  Repo path, e.g. "prompts/04_instagram_caption.md"

        Example:
            uploader.push_text(instagram_caption, dest="prompts/04_instagram_caption.md")
            uploader.push_text(substack_article,  dest="content/2026/02-buffett/article.md")
        """
        name = Path(dest).name
        msg  = commit_msg or f"Save {name} [{datetime.now().strftime('%Y-%m-%d')}]"
        b64  = base64.b64encode(text.encode("utf-8")).decode()

        self._push(dest, b64, msg)
        print(f"✅  {name}  →  {dest}")

    def push_story_pack(self, story_slug: str, files: dict, year: str = None):
        """
        Push a full story pack in one call.

        Args:
            story_slug:  e.g. "02-buffett-indicator"
            files:       {dest_suffix: local_path_or_text_string}
            year:        e.g. "2026". Defaults to current year.

        Example:
            uploader.push_story_pack("02-buffett-indicator", {
                "caption.md"    : instagram_caption,
                "article.md"    : substack_article,
                "chart_sq.png"  : "/content/chart_sq.png",
                "chart_pt.png"  : "/content/chart_pt.png",
            })
        """
        year = year or str(datetime.now().year)
        base = f"content/{year}/{story_slug}"
        print(f"\n☕  Pushing story pack → {base}/\n{'─'*50}")

        for suffix, source in files.items():
            dest = f"{base}/{suffix}"
            if isinstance(source, str) and os.path.exists(source):
                self.push_file(source, dest)
            elif isinstance(source, str):
                self.push_text(source, dest)
            else:
                print(f"⚠️  Skipped {suffix}: pass a file path or text string")

        print(f"{'─'*50}\n✅  Story pack complete\n")


# ============================================================================
# SUBSTACK PUBLISHER
# ============================================================================

class SubstackPublisher:
    """
    Publish draft and scheduled posts to Substack via their internal API.

    NOTE: Substack does not have an official public API. This uses the same
    endpoints their web app uses. It works as of early 2026 but may change
    if Substack updates their platform.

    Args:
        publication_url:  Your full Substack URL, e.g. "https://espressocharts.substack.com"
        email:            Your Substack login email
        password:         Your Substack login password
    """

    def __init__(self, publication_url: str, email: str, password: str):
        self.pub_url    = publication_url.rstrip("/")
        self.email      = email
        self.password   = password
        self.session    = requests.Session()
        self._logged_in = False

    def _login(self):
        """Authenticate and store session cookie."""
        if self._logged_in:
            return
        r = self.session.post(
            "https://substack.com/api/v1/email-login",
            json={"email": self.email, "password": self.password, "captcha_response": None},
        )
        if not r.ok:
            raise RuntimeError(f"Substack login failed {r.status_code}: {r.text}")
        self._logged_in = True
        print("✅  Logged in to Substack")

    def _markdown_to_html(self, text: str) -> str:
        """
        Markdown → HTML. Installs 'markdown' package if not present.
        """
        try:
            import markdown
        except ImportError:
            os.system("pip install markdown -q")
            import markdown
        return markdown.markdown(text, extensions=["extra", "nl2br"])

    def _create_post(self, title: str, body_html: str, subtitle: str = "") -> dict:
        """Create a post draft and return the post object."""
        self._login()
        r = self.session.post(
            f"{self.pub_url}/api/v1/posts",
            json={
                "type"          : "newsletter",
                "draft_title"   : title,
                "draft_subtitle": subtitle,
                "draft_body"    : body_html,
                "audience"      : "everyone",
            },
        )
        if not r.ok:
            raise RuntimeError(f"Failed to create post {r.status_code}: {r.text}")
        return r.json()

    # ── Public methods ────────────────────────────────────────────────────────

    def post_draft(self, title: str, body: str, subtitle: str = "", body_is_html: bool = False):
        """
        Save a post as a draft (not published, not scheduled).

        Args:
            title:        Post title
            body:         Post body in markdown (default) or HTML
            subtitle:     Optional subtitle shown in previews and email
            body_is_html: Set True if body is already HTML

        Example:
            substack.post_draft(
                title    = "The Buffett Indicator Just Hit 200%",
                subtitle = "What the stock market's favourite valuation metric is telling us",
                body     = substack_article,
            )
        """
        html = body if body_is_html else self._markdown_to_html(body)
        post = self._create_post(title, html, subtitle)
        print(f"✅  Draft saved: '{title}'")
        print(f"    Edit at: {self.pub_url}/publish/post/{post.get('id', '')}")
        return post

    def post_scheduled(self, title: str, body: str, publish_at: str,
                        subtitle: str = "", body_is_html: bool = False):
        """
        Create and schedule a post for future publication.

        Args:
            title:        Post title
            body:         Post body in markdown (default) or HTML
            publish_at:   UTC datetime string: "YYYY-MM-DDTHH:MM:SS"
                          Berlin is UTC+1 (CET, winter) or UTC+2 (CEST, summer).
                          For 9 AM Berlin CET  → use "08:00:00" UTC
                          For 9 AM Berlin CEST → use "07:00:00" UTC
            subtitle:     Optional subtitle shown in previews and email
            body_is_html: Set True if body is already HTML

        Example — Wednesday 9 AM Berlin (CET, winter):
            substack.post_scheduled(
                title      = "The Buffett Indicator Just Hit 200%",
                subtitle   = "What the stock market's favourite valuation metric is telling us",
                body       = substack_article,
                publish_at = "2026-02-25T08:00:00",
            )
        """
        self._login()
        html    = body if body_is_html else self._markdown_to_html(body)
        post    = self._create_post(title, html, subtitle)
        post_id = post["id"]

        r = self.session.post(
            f"{self.pub_url}/api/v1/posts/{post_id}/schedule",
            json={"post_date": f"{publish_at}Z"},
        )
        if not r.ok:
            raise RuntimeError(f"Failed to schedule post {r.status_code}: {r.text}")

        print(f"✅  Scheduled: '{title}'")
        print(f"    Publishes: {publish_at} UTC")
        print(f"    Edit at:   {self.pub_url}/publish/post/{post_id}")
        return r.json()

    def post_now(self, title: str, body: str, subtitle: str = "", body_is_html: bool = False):
        """
        Publish a post immediately.

        Example:
            substack.post_now(
                title    = "The Buffett Indicator Just Hit 200%",
                subtitle = "What the stock market's favourite valuation metric is telling us",
                body     = substack_article,
            )
        """
        self._login()
        html    = body if body_is_html else self._markdown_to_html(body)
        post    = self._create_post(title, html, subtitle)
        post_id = post["id"]

        r = self.session.post(f"{self.pub_url}/api/v1/posts/{post_id}/publish")
        if not r.ok:
            raise RuntimeError(f"Failed to publish {r.status_code}: {r.text}")

        print(f"✅  Published: '{title}'")
        print(f"    Live at: {self.pub_url}/p/{post.get('slug', '')}")
        return r.json()
