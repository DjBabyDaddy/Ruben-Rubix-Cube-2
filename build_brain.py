"""
build_brain.py — RUBE Super Brain compiler

Crawls AI framework documentation sites and compiles them into
RUBE_SUPER_BRAIN.md so RUBE's self-improvement pipeline can reason
against proven patterns when proposing code changes.

Powered by Firecrawl for reliable, JS-rendered doc site extraction.
"""

import os
from firecrawl import FirecrawlApp

BRAIN_OUTPUT = "RUBE_SUPER_BRAIN.md"

URLS = [
    "https://langchain-ai.github.io/langgraph/",
    "https://docs.crewai.com/",
    "https://modelcontextprotocol.io/specification/",
    "https://docs.anthropic.com/en/docs/build-with-claude/computer-use",
    "https://docs.llamaindex.ai/en/stable/",
]

def build_super_brain():
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        # Fall back to credentials file used by Firecrawl CLI
        import json, pathlib
        creds_path = pathlib.Path(os.environ.get("APPDATA", "")) / "firecrawl-cli" / "credentials.json"
        if creds_path.exists():
            with open(creds_path) as f:
                api_key = json.load(f).get("apiKey", "")

    if not api_key:
        print("❌ No FIRECRAWL_API_KEY found. Add it to .env or run: firecrawl init")
        return

    app = FirecrawlApp(api_key=api_key)

    print("🚀 Initializing RUBE Super Brain extraction via Firecrawl...")

    with open(BRAIN_OUTPUT, "w", encoding="utf-8") as f:
        f.write("# PROJECT RUBE: MASTER ARCHITECTURE KNOWLEDGE\n")
        f.write("INSTRUCTIONS: The following context is divided into XML tags. Always read the relevant <source> tags before generating system code or proposing logic.\n\n")

        for url in URLS:
            print(f"🧠 Assimilating: {url}")
            try:
                result = app.scrape_url(
                    url,
                    formats=["markdown"],
                    only_main_content=True,
                )
                content = result.get("markdown", "") if isinstance(result, dict) else getattr(result, "markdown", "")

                if content:
                    f.write(f"<source url='{url}'>\n")
                    f.write(content)
                    f.write("\n</source>\n\n")
                    print(f"  ✅ {len(content):,} chars extracted")
                else:
                    print(f"  ⚠️  No content returned for {url}")

            except Exception as e:
                print(f"  ❌ Failed: {url} — {e}")

    print(f"\n✅ Super Brain compiled → {BRAIN_OUTPUT}")


if __name__ == "__main__":
    build_super_brain()
