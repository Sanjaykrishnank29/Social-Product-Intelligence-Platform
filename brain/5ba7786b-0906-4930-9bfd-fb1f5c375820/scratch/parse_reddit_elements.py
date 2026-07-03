import sys
import re
from playwright.sync_api import sync_playwright

def parse_elements():
    print("Launching Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = "https://www.reddit.com/search/?q=amazon&sort=new"
        print(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            
            # Find all links
            links = page.locator("a").all()
            print(f"Found {len(links)} total links on page.")
            
            post_links = []
            for link in links:
                href = link.get_attribute("href") or ""
                if "/r/" in href and "/comments/" in href:
                    text = link.inner_text().strip().replace("\n", " ")
                    post_links.append((href, text))
            
            print(f"Found {len(post_links)} links containing /r/.../comments/:")
            for href, text in post_links[:15]:
                print(f"Href: {href} | Text: {text}")
                
            # Let's inspect the tags surrounding these links.
            # We can find the closest common parent or tags like <shreddit-post>, <article>, or dynamic divs.
            print("\nEvaluating potential post container elements:")
            
            # Check what other tag names exist in the page
            # Specifically shreddit-post, faceplate-tracker, etc.
            unique_tags = page.evaluate("() => Array.from(new Set(Array.from(document.querySelectorAll('*')).map(el => el.tagName.toLowerCase())))")
            reddit_custom_tags = [t for t in unique_tags if '-' in t or t in ['article', 'section']]
            print(f"Custom or container tags found: {reddit_custom_tags}")
            
            # Let's search for "search-telemetry-tracker"
            trackers = page.locator("search-telemetry-tracker").all()
            print(f"Found {len(trackers)} search-telemetry-tracker elements.")
            
            import json
            extracted = []
            for t in trackers:
                context_str = t.get_attribute("data-faceplate-tracking-context") or ""
                if not context_str:
                    continue
                try:
                    context = json.loads(context_str)
                    post_info = context.get("post", {})
                    profile_info = context.get("profile", {})
                    if not post_info:
                        continue
                        
                    post_id = post_info.get("id", "")
                    title = post_info.get("title", "")
                    author = profile_info.get("name", "anonymous")
                    
                    # Check if there is a subreddit
                    # The subreddit link usually has href starting with "/r/"
                    subreddit = "unknown"
                    subreddit_el = t.locator("a[href^='/r/']")
                    for sub in subreddit_el.all():
                        sub_href = sub.get_attribute("href") or ""
                        if "/comments/" not in sub_href:
                            subreddit = sub_href.split("/r/")[-1].split("/")[0]
                            break
                    
                    # Try to extract the post's text snippet if it has one
                    # Redesigned reddit search snippet is often inside faceplate-tracker or shreddit-search-result
                    # Let's look for paragraphs or span elements containing the text snippet.
                    # We can get innerText of a div or p within the tracker that is not the title
                    snippet = ""
                    snippet_el = t.locator("div[class*='text-neutral-content'] p, p[class*='text-neutral-content']")
                    if snippet_el.count() > 0:
                        snippet = snippet_el.first.inner_text().strip()
                    else:
                        # Fallback: find any paragraphs or divs containing text that isn't the title or subreddit
                        p_elements = t.locator("p").all()
                        for p in p_elements:
                            p_text = p.inner_text().strip()
                            if p_text and p_text != title and not p_text.startswith("r/") and not p_text.endswith("ago"):
                                snippet = p_text
                                break
                    
                    # Try to find date/timeago
                    time_el = t.locator("faceplate-timeago")
                    time_str = ""
                    if time_el.count() > 0:
                        time_el_time = time_el.first.locator("time")
                        if time_el_time.count() > 0:
                            time_str = time_el_time.first.get_attribute("datetime") or ""
                            
                    extracted.append({
                        "id": post_id,
                        "title": title,
                        "author": author,
                        "subreddit": subreddit,
                        "snippet": snippet,
                        "time": time_str
                    })
                except Exception as inner_e:
                    pass
            
            # De-duplicate by post_id
            seen_ids = set()
            unique_extracted = []
            for p in extracted:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    unique_extracted.append(p)
                    
            print(f"Extracted {len(unique_extracted)} unique posts:")
            for idx, p in enumerate(unique_extracted[:10]):
                # print safely using string formatting to avoid encoding errors
                title_safe = p["title"].encode('ascii', 'ignore').decode('ascii')
                snippet_safe = p["snippet"].encode('ascii', 'ignore').decode('ascii')
                print(f"{idx}: ID={p['id']} | Sub={p['subreddit']} | Author={p['author']} | Time={p['time']}")
                print(f"   Title: {title_safe}")
                print(f"   Snippet: {snippet_safe}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        browser.close()





if __name__ == "__main__":
    parse_elements()
