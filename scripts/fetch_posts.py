"""
SpaceCatX WordPress 글 동기화 스크립트

- WordPress REST API(wp-json/wp/v2/posts)에서 공개(published) 글 전체를 가져온다.
- per_page=100 + X-WP-TotalPages 헤더로 페이지네이션 처리.
- 각 글마다:
    - posts/{slug}.md   : content.rendered를 Markdown으로 변환한 AI 열람용 파일
    - raw/{slug}.html   : content.rendered HTML 원본 그대로 저장
- index.json에는 id, slug, title, url, published, modified, excerpt만 저장.
- 카테고리 매핑, 삭제/비공개 글 정리는 MVP 범위 밖이라 생략.
"""

import json
import os
import re
from html import unescape

import requests
from markdownify import markdownify as md

BASE_URL = "https://spacecatx.me/wp-json/wp/v2/posts"
POSTS_DIR = "posts"
RAW_DIR = "raw"
INDEX_FILE = "index.json"
PER_PAGE = 100


def strip_html(html_text: str) -> str:
    """excerpt 등 짧은 HTML에서 태그만 제거."""
    return unescape(re.sub(r"<[^<]+?>", "", html_text)).strip()


def fetch_all_posts():
    """공개(published) 글 전체를 페이지네이션으로 가져온다."""
    posts = []
    page = 1

    while True:
        resp = requests.get(
            BASE_URL,
            params={
                "per_page": PER_PAGE,
                "page": page,
                "status": "publish",
                "orderby": "id",
                "order": "asc",
            },
            timeout=30,
        )

        if resp.status_code == 400:
            break
        resp.raise_for_status()

        batch = resp.json()
        if not batch:
            break

        posts.extend(batch)

        total_pages = int(resp.headers.get("X-WP-TotalPages", "1"))
        if page >= total_pages:
            break
        page += 1

    return posts


def save_post(post: dict) -> dict:
    """개별 글을 md/html로 저장하고 index용 요약 dict를 반환."""
    slug = post["slug"]
    title = unescape(post["title"]["rendered"])
    url = post["link"]
    published = post["date"]
    modified = post["modified"]
    excerpt = strip_html(post.get("excerpt", {}).get("rendered", ""))
    content_html = post["content"]["rendered"]

    with open(os.path.join(RAW_DIR, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(content_html)

    content_md = md(content_html, heading_style="ATX")
    md_output = (
        f"# {title}\n\n"
        f"- URL: {url}\n"
        f"- Published: {published}\n"
        f"- Modified: {modified}\n\n"
        f"---\n\n"
        f"{content_md}\n"
    )

    with open(os.path.join(POSTS_DIR, f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write(md_output)

    return {
        "id": post["id"],
        "slug": slug,
        "title": title,
        "url": url,
        "published": published,
        "modified": modified,
        "excerpt": excerpt,
    }


def main():
    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(RAW_DIR, exist_ok=True)

    posts = fetch_all_posts()

    index = [save_post(post) for post in posts]
    index.sort(key=lambda p: p["published"], reverse=True)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"동기화 완료: 총 {len(posts)}건")


if __name__ == "__main__":
    main()
