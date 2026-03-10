# Medium Draft Bot

A fully automated tool to convert local Markdown files into formatted Medium drafts, bypassing Cloudflare Turnstile and saving you hours of manual formatting.

With the depreciation of Medium's REST API, this tool employs a headless browser (Playwright) to inject HTML smoothly into your Medium editor, natively triggering their auto-save mechanisms as if you typed it yourself.

## Prerequisites
- **Docker** (For everyday seamless, headless usage)
- **uv** (Optional: For local execution if you want to see the UI via `--headed`)

## How to Format Your Markdown
You can format your file using standard Markdown!

The script reads your `.md` file and converts it into HTML using the Python `markdown` library. When injected into Medium's editor, it perfectly maps up to Medium's styling.

Supported formatting:
- `# Headers` (H1, H2, H3, etc.)
- `**Bold**` and `*Italic*` Text
- `[Links](url)`
- `> Blockquotes`
- Lists (ordered and unordered)
- `Inline Code`
- ```Code Blocks```
- `![Images](https://raw.githubusercontent.com/.../image.png)`

> **⚠️ Important Image Rule**: Local images (e.g., `./image.png`) will **not upload**. Medium needs a public URL to fetch the image. Host your images in a public GitHub repo or an image host, and provide the raw public URL in your document. Medium will automatically download and embed it into your draft permanently.

## Usage

### 0. Git Usage (What to Push)
Make sure you add a `.gitignore` to prevent leaking your auth tokens!

**Files to Push:**
- `draft.py`
- `login.py`
- `draft.sh`
- `requirements.txt`
- `README.md`
- `Dockerfile` (Optional)

**Files to Avoid (Add to `.gitignore`):**
- `medium_state.json` (CRITICAL: This contains your literal Medium auth keys!)
- `.venv/`
- Any `__pycache__` directories
- Any local article drafts (`*.md` / `*.html` and output `*.png` screenshots) you don't want public yet.

### 1. Generating Auth State (First Time Only)
Medium is protected by Cloudflare Turnstile. We must generate a valid session state using a headed browser first.

Run the login script locally to bypass the bot-check and log in:
```bash
uv run python login.py
```
After successfully logging in, it saves your cookies and auth keys into `medium_state.json`. Do not commit this file.

### 2. Creating a Draft (Docker/Headless)
For daily usage, the easiest way is checking your markdown document with the included bash wrapper. This builds and runs a lightweight headless Docker container.

```bash
./draft.sh your_awesome_article.md
```
*Note: You can pass absolute paths! E.g. `./draft.sh /home/user/Documents/blog_post.md`*

If successful, the output will give you the direct URL to your saved draft! (`https://medium.com/p/.../edit`)

### 3. Seeing the Execution (Headed UI Mode)
If you want to watch the bot type and inject the HTML in real-time, you must run it locally on your machine rather than inside Docker. We've added a `--headed` flag specifically for this:

1. Sync local dependencies: `uv sync`
2. Install Chromium binaries for Playwright: `uv run playwright install chromium`
3. Run the draft script with the headed flag:
```bash
uv run python draft.py your_awesome_article.md --headed
```

## How It Works Under The Hood
1. Playwright launches (stealth applied) using your `medium_state.json`.
2. It hits `/new-story` and simulates human typing your article title.
3. This keystroke triggers Medium's React `onChange` listeners, which fires an API call to the backend to create the draft and generates a unique Story ID.
4. With the story shell ready, the script generates a `ClipboardEvent` padded with your markdown's compiled HTML payload.
5. It forcefully dispatches this `paste` event into the editor.
6. Medium's native Draft.js catches the paste, formats the HTML payload into Medium blocks, and instantly auto-saves the complete article.
