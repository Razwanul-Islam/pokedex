# Bringing the Pokédex to Living World

A simple web app that transforms images of real-world objects or living things into their own "Pokémon" with generated descriptions, just like a Pokédex! 🚀


## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact](#contact)

## About the Project

As an anime enthusiast and a big fan of Pokémon, I wanted to recreate the magic of the Pokédex in the real world. This web app takes an image input and uses an LLM to provide fun, Pokémon-like information about the object in the picture.

## Features

- **Image Upload**: Upload any image of a real-world object or living thing.
- **Pokémon Description**: Get a generated description as if the object were a Pokémon.
- **Simple Interface**: Easy-to-use frontend with HTML, CSS, and JavaScript.
- **Fast Processing**: Quick response times using the Gemini-1.5-flash LLM.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Django, Django Rest Framework
- **AI Model**: Gemini-1.5-flash LLM (via Google's free API)

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- **Python 3.x** installed on your machine
- **pip** package installer
- **Git** for cloning the repository

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Razwanul-Islam/pokedex.git
   cd pokedex
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**

   - Create a `.env` file in the project root.
   - Add your Google API credentials:

     ```env
     GEMENI_API_KEY=your_google_api_key
     ```

6. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

7. **Run the server**

   ```bash
   python manage.py runserver
   ```

8. **Access the app**

   Open your web browser and navigate to `http://localhost:8000`.

## Usage

1. **Upload an Image**

   Click on the "Upload Image" button and select an image from your device.

2. **Generate Pokémon Info**

   After successful image upload automatically generate the info

3. **Enjoy and Share**

   Read the fun description and share it with your friends!

## Contributing

Contributions are welcome! Feel free to fork the repository and make improvements or add new features.

1. **Fork the Project**
2. **Create your Feature Branch**

   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **Commit your Changes**

   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. **Push to the Branch**

   ```bash
   git push origin feature/AmazingFeature
   ```

5. **Open a Pull Request**


## Contact

- **LinkedIn**: [Md. Razwanul Islam](https://www.linkedin.com/in/md-razwanul-islam-2349311b0/)
- **Email**: razwanrakib0@gmail.com

---

Let's inspire each other to learn, create, and have fun. If you have more ideas like this, please share them with me. Let's build it together!