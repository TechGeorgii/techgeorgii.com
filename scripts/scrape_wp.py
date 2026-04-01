#!/usr/bin/env python3
"""Fetch WP posts + about page, save Markdown + downloaded images under src/pages/<slug>/."""

from __future__ import annotations

import html as html_lib
import json
import os
import re
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = "https://techgeorgii.com"
OUT = Path(__file__).resolve().parent.parent / "src" / "pages"
SKIP_SLUGS = {"erc-2612-tutorial-and-adoption-research"}

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "TechGeorgii-site-migration (local)"


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def plain_title(rendered: str) -> str:
    return html_lib.unescape(BeautifulSoup(rendered, "html.parser").get_text())


def plain_excerpt(rendered: str) -> str:
    t = BeautifulSoup(rendered, "html.parser").get_text()
    t = " ".join(t.split())
    return t[:220] if t else ""


def sanitize_filename(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    name = os.path.basename(urllib.parse.unquote(path))
    if not name or name == "/":
        name = "image.bin"
    return re.sub(r"[^\w.\-]", "_", name)


def is_local_asset(url: str) -> bool:
    if not url or url.startswith("data:"):
        return False
    host = urllib.parse.urlparse(url).netloc
    return host in ("", "techgeorgii.com", "www.techgeorgii.com")


def resolve_url(src: str) -> str:
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return BASE.rstrip("/") + src
    return src


def download_images(soup: BeautifulSoup, folder: Path) -> None:
    used: set[str] = set()

    def alloc_name(url: str) -> str:
        base = sanitize_filename(url)
        name = base
        i = 1
        while name in used:
            stem, ext = os.path.splitext(base)
            name = f"{stem}-{i}{ext}"
            i += 1
        used.add(name)
        return name

    for img in soup.find_all("img"):
        src = img.get("src") or ""
        src = resolve_url(src.strip())
        if not is_local_asset(src):
            continue
        try:
            r = SESSION.get(src, timeout=90)
            r.raise_for_status()
            fn = alloc_name(src)
            (folder / fn).write_bytes(r.content)
            img["src"] = "./" + fn
        except Exception as e:
            print("  warn: image skip", src, e)
            continue
        for a in ("srcset", "sizes", "loading", "decoding", "width", "height", "class"):
            img.attrs.pop(a, None)


def fix_internal_links(md: str) -> str:
    md = md.replace(
        "](/uniswap-v3-sdk-tutorial-part-1--load-token-balances)",
        "](/uniswap-v3-sdk-tutorial-part-1-load-token-balances/)",
    )
    md = md.replace(
        "](/uniswap-v3-sdk-swap-tutorial-part-3-get-quotes-with-uniswap-quoter)",
        "](/uniswap-v3-sdk-swap-tutorial-part-3-get-quotes-with-uniswap-quoter/)",
    )
    return md


def _code_lang_from_el(code) -> str:
    if not code:
        return ""
    lang = (code.get("lang") or "").strip().lower()
    if lang:
        return lang
    for c in code.get("class") or []:
        if isinstance(c, str) and c.startswith("language-"):
            return c.replace("language-", "", 1).split()[0].lower()
    return ""


def _normalize_shiki_lang(lang: str) -> str:
    if not lang:
        return "text"
    aliases = {
        "plaintext": "text",
        "plain": "text",
        "console": "bash",
        "shell": "bash",
        "sh": "bash",
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "yml": "yaml",
    }
    return aliases.get(lang, lang)


def html_to_markdown(fragment: str) -> str:
    soup = BeautifulSoup(fragment, "html.parser")
    for bad in soup.find_all(["script", "style", "iframe"]):
        bad.decompose()

    pres: list[tuple[str, str]] = []
    for pre in soup.find_all("pre"):
        code = pre.find("code")
        raw_lang = _code_lang_from_el(code)
        lang = _normalize_shiki_lang(raw_lang)
        raw = code.get_text() if code else pre.get_text()
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        pres.append((lang, raw))
        idx = len(pres) - 1
        mark = f"TGCBLOCK{idx}PLACEHOLDER"
        pre.replace_with(BeautifulSoup(f"<p>{mark}</p>", "html.parser"))

    text = md(
        str(soup),
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
    )
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"

    for i, (lang, raw) in enumerate(pres):
        body = raw.rstrip() + "\n"
        fence = f"```{lang}\n{body}```"
        text = text.replace(f"TGCBLOCK{i}PLACEHOLDER", fence)

    return text


def write_post(item: dict) -> dict:
    slug = item["slug"]
    if slug in SKIP_SLUGS:
        print("skip", slug)
        return {}

    folder = OUT / slug
    folder.mkdir(parents=True, exist_ok=True)

    title = plain_title(item["title"]["rendered"])
    raw_html = item["content"]["rendered"]
    soup = BeautifulSoup(raw_html, "html.parser")
    download_images(soup, folder)

    body_md = fix_internal_links(html_to_markdown(str(soup)))
    desc = plain_excerpt(item.get("excerpt", {}).get("rendered", ""))
    date = (item.get("date") or "")[:10]

    fm = ["---", "layout: ../../layouts/ArticleLayout.astro", f"title: {yaml_str(title)}"]
    if desc:
        fm.append(f"description: {yaml_str(desc)}")
    if slug != "about-me" and date:
        fm.append(f'pubDate: "{date}"')
    fm.append("---\n")

    (folder / "index.md").write_text("\n".join(fm) + "\n" + body_md, encoding="utf-8")
    print("wrote", slug)
    return {"title": title, "href": f"/{slug}/", "date": date}


def main() -> None:
    posts = SESSION.get(f"{BASE}/wp-json/wp/v2/posts", params={"per_page": 100}, timeout=60).json()
    pages = SESSION.get(f"{BASE}/wp-json/wp/v2/pages", params={"slug": "about-me"}, timeout=60).json()

    index_entries: list[dict] = []

    for p in sorted(posts, key=lambda x: x["date"], reverse=True):
        e = write_post(p)
        if e:
            index_entries.append(e)

    for p in pages:
        write_post(p)

    all_for_nav = [
        {
            "title": "ERC-2612 tutorial and adoption research",
            "href": "/erc-2612-tutorial-and-adoption-research/",
            "date": "2024-02-17",
        }
    ] + [x for x in index_entries if x.get("href") != "/about-me/"]
    all_for_nav.sort(key=lambda x: x["date"], reverse=True)

    index_astro = f'''---
import BaseLayout from "../layouts/BaseLayout.astro";

const posts = {json.dumps(all_for_nav, ensure_ascii=False, indent=2)} as const;
---
<BaseLayout title="TechGeorgii" description="Ethereum, Solidity, Uniswap, ethers.js articles">
  <h1>TechGeorgii</h1>
  <p>Ethereum, Solidity, Uniswap, ethers.js — notes and tutorials.</p>
  <ul class="post-index">
    {{posts.map((p) => (
      <li>
        <time datetime={{p.date}}>{{p.date}}</time>
        <a href={{p.href}}>{{p.title}}</a>
      </li>
    ))}}
  </ul>
</BaseLayout>
'''
    (OUT / "index.astro").write_text(index_astro, encoding="utf-8")
    print("updated index.astro")


if __name__ == "__main__":
    main()
