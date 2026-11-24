# Pokédex Scanner

Pokédex Scanner is a Django web application that turns an uploaded image into a generated, Pokédex-style field guide entry. It accepts images of Pokémon or real-world subjects and uses Google's Gemini model to produce structured details for the scanner interface.

## Overview

The home page provides a responsive image scanner. Its upload control supports click, keyboard, and drag-and-drop selection; includes labels and instructions for the file input; exposes loading and result updates through live regions; provides visible keyboard focus styles; and respects reduced-motion preferences. The application sends the image to the server, displays a preview while it is analyzed, and renders the returned entry when processing is complete.

## Features

- Image selection through click, keyboard, and drag-and-drop interactions
- Image preview and live loading status
- Server-side multipart image upload endpoint at `POST /generate-info/`
- Gemini-powered generation of Pokédex-style details, including description, abilities, habitat, moves, and more
- Automatic saving of successful scans and their uploaded images to a shared collection book at `/collection/`
- Session-specific mock battles at `/battle/`, using a saved scan against a rules-based Pikachu; no AI service is needed for battle turns
- “Scan another image” action that opens the file picker; cancelling keeps the current result visible
- Responsive styles, keyboard focus indicators, and reduced-motion support
- Django tests that check the rendered scanner markup and expected inline JavaScript

## Technology Stack

| Area | Technology |
| --- | --- |
| Web framework | Django 5.1 |
| API handling | Django REST Framework |
| Templates | Django Templates |
| AI integration | Google Generative AI with `gemini-1.5-flash` |
| Image handling | Pillow |
| Database | SQLite |
| Frontend | HTML, CSS, and inline JavaScript |

## Prerequisites

- Python 3
- `pip`
- Git, to clone the repository
- A Google API key with access to the Gemini API

## Setup

1. Clone the repository and enter its directory:

   ```bash
   git clone https://github.com/Razwanul-Islam/pokedex.git
   cd pokedex
   ```

   If you already have a checkout, run the remaining commands from its root directory.

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   On Windows, activate it with:

   ```bat
   venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add your API key:

   ```env
   GEMENI_API_KEY=your_google_api_key
   ```

   The setting name is `GEMENI_API_KEY`, matching the application configuration.

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

## Run Locally

Start Django's development server:

```bash
python manage.py runserver
```

Open `http://localhost:8000/` in a browser, then upload an image to generate an entry.

Successful scans are saved automatically and visible to everyone using this application. Images are stored under `media/`, while their generated data is stored in the database. Keep both when backing up or moving the application. Django serves the media files in development; a deployment must configure its web server or storage backend to serve `MEDIA_URL` from `MEDIA_ROOT`.

## Tests

Run the Django test suite with:

```bash
python manage.py test
```

Tests cover scanner markup and JavaScript strings, saving and revisiting a scan with a mocked Gemini response and temporary image storage, and mock battle behavior. They do not execute JavaScript in a browser or call the Gemini API.

## Project Structure

```text
.
├── core/                 # Application views and tests
├── pokedex/              # Django settings and URL configuration
├── static/css/           # Scanner styles
├── templates/            # Django templates
├── manage.py             # Django management entry point
├── requirements.txt      # Python dependencies
└── db.sqlite3            # Local SQLite database created by migrations
```

## Contributing

Contributions are welcome. Fork the repository, create a focused feature branch, make and test your changes, then open a pull request describing the change.

Before submitting, run:

```bash
python manage.py test
```
