import sys
from playwright.sync_api import sync_playwright

def test_reddit():
    print("Launching Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Setup context with normal browser user agent to avoid instant blocking
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Test old.reddit.com search which is very clean and easy to scrape
        url = "https://old.reddit.com/search/?q=amazon&sort=new"
        print(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="load", timeout=20000)
            print("Page loaded successfully.")
            
            # Wait for search results container
            # old.reddit posts are inside div.thing
            posts = page.locator("div.thing").all()
            print(f"Found {len(posts)} posts on old.reddit search page.")
            
            results = []
            for post in posts[:5]:
                title_el = post.locator("a.title")
                title = title_el.inner_text() if title_el.count() > 0 else "N/A"
                author_el = post.locator("a.author")
                author = author_el.inner_text() if author_el.count() > 0 else "N/A"
                time_el = post.locator("time")
                time_val = time_el.get_attribute("datetime") if time_el.count() > 0 else "N/A"
                results.append({"title": title, "author": author, "time": time_val})
                
            print("Extracted items:")
            for r in results:
                print(r)
                
        except Exception as e:
            print(f"Error occurred during old.reddit load/parse: {e}")
            
        # Also test new www.reddit.com
        url_new = "https://www.reddit.com/search/?q=amazon&sort=new"
        print(f"\nNavigating to {url_new}...")
        try:
            page.goto(url_new, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000) # wait a bit for dynamic page rendering
            print("Page loaded successfully.")
            
            # Print page title
            print(f"Page Title: {page.title()}")
            
            # Check for blocking signs like 'verify you are human' or h1 with error
            body_text = page.locator("body").inner_text()
            if "verify you are human" in body_text.lower() or "blocked" in body_text.lower():
                print("WARNING: Modern Reddit blocked the crawler or prompted for Cloudflare verification.")
            else:
                # Let's see if we can find post elements
                # Modern reddit has search post tags
                # Typically, posts have attributes like data-testid="post-title" or <shreddit-post> or similar tags depending on the redesigned UI version
                shreddit_posts = page.locator("shreddit-post").all()
                print(f"Found {len(shreddit_posts)} shreddit-post elements.")
                if len(shreddit_posts) == 0:
                    # Alternative selectors
                    post_titles = page.locator("a[data-click-id='body']").all()
                    print(f"Found {len(post_titles)} click-id body links.")
        except Exception as e:
            print(f"Error occurred during new reddit load/parse: {e}")
            
        browser.close()

if __name__ == "__main__":
    test_reddit()
