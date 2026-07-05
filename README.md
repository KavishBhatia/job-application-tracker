# Job Application Tracker

A small, personal web app for keeping track of job applications: who you applied to, what role, what stage you're at, and how interviews are going. No account sign-up, no cloud service, no subscription — it runs on your own computer and keeps your data in a single file that stays with you.

## What it does

Think of it as a private spreadsheet that fills itself in and looks nicer.

- **Add an application by typing a sentence.** Write something like *"Applied at Acme Corp for a Backend Engineer role"* and the app figures out the company and role for you (using Google's Gemini AI). You just confirm the details before saving.
- **Track the status of each application.** Applied, Interviewing, Offer, Rejected, or Withdrawn — change it any time from a simple dropdown.
- **Keep notes on interview progress.** How many rounds an application has, which round you're currently on, and any feedback you've received — click on an application to open it up and fill these in.
- **Export and import your list.** Download everything as a CSV or Excel file (handy for backups or sharing), and re-import a file later without creating duplicate entries.
- **Light and dark mode**, matching your system automatically or switchable by hand.
- **Your data stays yours.** Everything is stored locally in a small database file on your own machine — nothing is sent anywhere except the one sentence you type, which goes to Google's Gemini service just long enough to figure out the company and role.

## What it looks like, page by page

The app has three simple pages, with a menu at the top to jump between them:

1. **Add Application** — the page you land on. Type a sentence describing what you applied to, optionally paste a link to the job posting, and continue.
2. **Applications** — the full list of everything you've logged, newest and most active first. Click any row to see and edit its interview rounds and feedback.
3. **Import / Export** — download your list as a spreadsheet, or upload one to bring data back in.

## Running it on your own computer

This app isn't hosted anywhere online — you run it yourself. Don't worry if you've never done this before; it's a handful of commands typed into a terminal, done once.

### What you'll need

- A computer with **Python 3.11 or newer** installed.
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/) — a tool that installs the app's dependencies for you. Follow the link for a one-line install command for your operating system.
- *(Optional)* A free **Gemini API key** from [ai.google.dev](https://ai.google.dev/) if you want the "type a sentence" auto-fill feature. Without it, the app still works perfectly — you just type the company and role in yourself.

### Steps

1. **Download the project.** If you have `git`, run:
   ```bash
   git clone https://github.com/KavishBhatia/job-application-tracker.git
   cd job-application-tracker
   ```
   (Or use GitHub's "Download ZIP" button and unzip it, then open a terminal in that folder.)

2. **Install everything the app needs:**
   ```bash
   uv sync
   ```

3. *(Optional)* **Add your Gemini API key**, if you got one:
   ```bash
   cp .env.example .env
   ```
   Then open the new `.env` file in any text editor and paste your key in.

4. **Start the app:**
   ```bash
   uv run uvicorn src.app:app --reload
   ```

5. **Open it in your browser:** go to [http://localhost:8000](http://localhost:8000)

That's it — the app is now running locally. To stop it, go back to the terminal and press `Ctrl+C`. To start it again later, repeat step 4 from inside the project folder.

Your applications are saved in a file at `data/job_applications.db`, which is created automatically the first time you run the app. Back it up like any other file if you want to keep a copy.

### Even easier: a desktop launcher

If you did the one-time setup above (steps 1–2), you don't have to open a terminal every time. You can create a **"Job Application Tracker"** launcher app on the Desktop — double-click it and it starts the server in the background and opens the app in your browser automatically. Clicking it again while the app is already running just reopens the browser tab, it won't start a second copy.

It's built from `scripts/start_app.sh` (compiled into an app with macOS's `osacompile` + `scripts/start_app.applescript`). Before compiling, update the script path inside `scripts/start_app.applescript` to match where you cloned this repo, then run:

    osacompile -o ~/Desktop/"Job Application Tracker.app" scripts/start_app.applescript

Server logs for the launcher live at `data/server.log` if you ever need to see what happened after double-clicking.

## For developers

- **Stack**: Python, [FastAPI](https://fastapi.tiangolo.com/) for the web server, [Jinja2](https://jinja.palletsprojects.com/) for HTML templates, plain SQLite for storage (no ORM), vanilla CSS/JS (no frontend framework or build step).
- **Dependency management**: [uv](https://docs.astral.sh/uv/), see `pyproject.toml`.
- **Run the test suite**:
  ```bash
  uv run pytest
  ```
- **Project layout**:
  ```text
  src/
  ├── app.py              # FastAPI app setup
  ├── db.py                # SQLite persistence, schema + migrations
  ├── models.py             # Data shapes (status values, etc.)
  ├── utils.py               # Small shared helpers
  ├── llm/gemini_client.py    # Sentence -> company/role parsing via Gemini
  ├── io_formats/             # CSV / Excel export & import
  ├── routes/                 # Page and form-handling routes
  └── templates/               # HTML pages (Jinja2)
  tests/                        # Unit + integration tests
  ```
- **Design system**: see `PRODUCT.md` and `DESIGN.md` for the color palette, typography, and UI conventions used throughout the app.
- **Feature history**: this project was built feature-by-feature using [GitHub's spec-kit](https://github.com/github/spec-kit) workflow; see the `specs/` folder for each feature's spec, plan, and task breakdown.

## Privacy note

The only data that ever leaves your computer is the free-text sentence you type when adding an application (sent to Google's Gemini API solely to extract the company and role, if you've configured an API key). Everything else — your applications, statuses, notes, and exported files — stays on your machine.
