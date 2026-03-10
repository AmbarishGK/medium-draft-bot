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

## Usage: End-to-End Onboarding

### 1. First-Time Setup (Once per machine)

First, install the dependencies required for the initial login:
```bash
# Install Playwright and its browser binaries
uv sync
uv run playwright install chromium
```

Next, you must generate your Medium Auth Token file so the bot can act as you. We do this by launching a visible browser so you can solve any Cloudflare Turnstile checks or input your 2FA codes.
```bash
uv run python login.py
```
*A browser window will open. Log into Medium normally. Once you are fully logged in and see the homepage, close the window. The script will save your session to `medium_state.json`. You never have to do this again unless your session expires.*

---

### 2. The Daily Workflow (Every time you write a post)

Now that you are authenticated, you are ready to use the bot every day!

**Step A: Write Your Article**
Create a new file (e.g., `my_cool_article.md` or `.html`). Write your article using standard Markdown or HTML.

**Step B: Run the Bot**
Whenever you are finished writing and want to send it to Medium, simply run the bash script!
```bash
./draft.sh my_cool_article.md
```
*Note: This script automatically uses Docker (Playwright official image) to execute the Python logic safely without touching your host system, other than reading your article and state file.*

**Step C: Final Review**
The script will print the success URL (e.g., `https://medium.com/p/12345/edit`). Click the link to review your perfectly formatted draft in the Medium editor, add your 5 Medium tags, and hit the green **Publish** button!

---

### 3. Optional: Seeing the Execution (Headed UI Mode)
If you want to watch the bot type and inject the HTML in real-time, you must run it locally on your python environment rather than inside Docker. We've added a `--headed` flag specifically for this:

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
