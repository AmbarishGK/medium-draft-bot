import sys, markdown
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def run(file_path, headed=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # If Markdown, compile to HTML. Otherwise, assume it's already HTML.
    if file_path.lower().endswith('.md'):
        html = markdown.markdown(content)
    else:
        html = content
    
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(headless=not headed)
        context = browser.new_context(
            storage_state="medium_state.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = context.new_page()
        # Setup response logging to see if Medium's save API returns 403
        page.on("response", lambda response: print(f"Response: {response.url} - {response.status}") if not response.ok else None)

        page.goto("https://medium.com/new-story")
        
        try:
            title = page.locator('[contenteditable="true"]').first
            title.wait_for(timeout=10000)
            title.click()
            page.wait_for_timeout(500)
            page.keyboard.type("New Draft", delay=100)
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            
            # Wait for the story to actually be created (URL changes from /new-story to /p/...)
            print("Waiting for initial story creation...")
            page.wait_for_timeout(5000)
            print(f"URL after typing title: {page.url}")
            
            # Inject HTML by simulating a paste event directly on the active element
            paste_script = """(html) => {
                const dataTransfer = new DataTransfer();
                dataTransfer.setData('text/html', html);
                dataTransfer.setData('text/plain', 'fallback text');
                
                const pasteEvent = new ClipboardEvent('paste', {
                    clipboardData: dataTransfer,
                    bubbles: true,
                    cancelable: true
                });
                
                document.activeElement.dispatchEvent(pasteEvent);
            }"""
            page.evaluate(paste_script, html)
            
            # Wait 8 seconds for Medium's background auto-save
            page.wait_for_timeout(8000)
            page.screenshot(path="/out/success_screenshot.png")
            print(f"\n✅ Success! Draft URL: {page.url}\n")
        except Exception as e:
            page.screenshot(path="/out/debug_screenshot.png")
            print(f"Failed! URL: {page.url}. Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upload Markdown to Medium as a Draft")
    parser.add_argument("md_path", help="Path to your markdown file")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser UI (requires local environment)")
    args = parser.parse_args()
    
    run(args.md_path, args.headed)
