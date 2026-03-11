import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def build_super_brain():
    # Paste your 20 URLs here
    urls = [
        "https://langchain-ai.github.io/langgraph/",
        "https://docs.crewai.com/",
        "https://modelcontextprotocol.io/specification/",
        "https://docs.anthropic.com/en/docs/build-with-claude/computer-use",
        "https://docs.llamaindex.ai/en/stable/"
        # ... add the rest ...
    ]
    
    # PRO TWEAK: Strip out useless tokens (links, images, nav bars)
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(
            options={
                "ignore_links": True,  # Saves thousands of tokens
                "ignore_images": True, # Removes broken ![alt] tags
                "escape_html": True
            }
        )
    )

    print("🚀 Initializing Project Rube Brain Extraction...")
    
    async with AsyncWebCrawler() as crawler:
        with open("RUBE_SUPER_BRAIN.md", "w", encoding="utf-8") as f:
            # Setting the overarching system instructions
            f.write("# PROJECT RUBE: MASTER ARCHITECTURE KNOWLEDGE\n")
            f.write("INSTRUCTIONS: The following context is divided into XML tags. Always read the relevant <source> tags before generating system code or proposing logic.\n\n")
            
            for url in urls:
                print(f"🧠 Assimilating: {url}")
                result = await crawler.arun(url=url, config=config)
                
                if result.success:
                    # PRO TWEAK: Wrapping in XML tags for Anthropic models
                    f.write(f"<source url='{url}'>\n")
                    f.write(result.markdown)
                    f.write("\n</source>\n\n")
                else:
                    print(f"❌ Failed to scrape: {url} - {result.error_message}")

    print("✅ Super Brain compiled successfully into RUBE_SUPER_BRAIN.md")

if __name__ == "__main__":
    asyncio.run(build_super_brain())