from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def run_login():
    with Stealth().use_sync(sync_playwright()) as p:
        # headless=False so you can see it, channel="chrome" uses your real browser
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context()
        page = context.new_page()
        
        page.goto("https://medium.com/")
        
        print("\n*** ACTION REQUIRED ***")
        print("1. Use the opened browser window to log into Medium manually.")
        print("2. Wait until you are fully logged in and see your homepage.")
        print("3. Return to this terminal and press ENTER to save your session.\n")
        
        input("Press ENTER here when done logging in...")
        
        # Save the authenticated state
        context.storage_state(path="medium_state.json")
        print("Saved to medium_state.json!")
        browser.close()

if __name__ == "__main__":
    run_login()
