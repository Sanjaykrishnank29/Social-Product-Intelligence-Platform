import sys
from playwright.sync_api import sync_playwright

def debug_reddit():
    print("Launching Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # Check old.reddit
        url = "https://old.reddit.com/search/?q=amazon&sort=new"
        print(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="load", timeout=20000)
            title = page.title()
            print(f"old.reddit Page Title: {title}")
            body_text = page.locator("body").inner_text()
            print(f"old.reddit Body snippet (first 1000 chars):\n{body_text[:1000]}")
            
            # Check if there is an error page or a captcha or cloudflare
            if "blocked" in body_text.lower() or "verify" in body_text.lower() or "robot" in body_text.lower():
                print("--> BLOCKED on old.reddit!")
        except Exception as e:
            print(f"Error old.reddit: {e}")
            
        # Check new reddit
        url_new = "https://www.reddit.com/search/?q=amazon&sort=new"
        print(f"\nNavigating to {url_new}...")
        try:
            page.goto(url_new, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(3000)
            title = page.title()
            print(f"new reddit Page Title: {title}")
            body_text = page.locator("body").inner_text()
            print(f"new reddit Body snippet (first 1000 chars):\n{body_text[:1000]}")
            
            if "blocked" in body_text.lower() or "verify" in body_text.lower() or "robot" in body_text.lower():
                print("--> BLOCKED on new reddit!")
        except Exception as e:
            print(f"Error new reddit: {e}")
            
        browser.close()

if __name__ == "__main__":
    debug_reddit()
