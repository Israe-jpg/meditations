# Meditations

Flask application built with Flask and the Clean Blog template provided by Bootstrap.

## Features

- **Displaying well-being related content** (meditations and exercise) in the form of posts with dynamic content loading
- **Mobile friendly design** due to Bootstrap design
- **Contact form** made with SMTP with email notifications of the information provided by users
- **Blog posts loaded** with external API, created with npoint.io
- **Clean and minimalistic design** suited for the main theme of the website

## Prerequisites

- Python 3.7 or higher
- pip
- Git

## Installation

1. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
meditations/
├── server.py
├── requirements.txt
├── data/
│   └── blog-data.txt
├── static/
│   ├── styles.css
│   ├── script.js
│   └── background.jpg
└── templates/
    ├── index.html
    ├── about.html
    ├── contact.html
    ├── post.html
    ├── header.html
    └── footer.html
```

## Usage

1. **Start the development server**

   ```bash
   python server.py
   ```

2. **Open your browser**
   Navigate to `http://localhost:5000`

## Acknowledgments

- [Bootstrap Clean Blog Theme](https://startbootstrap.com/theme/clean-blog) for the beautiful design
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [npoint.io](https://npoint.io/) for the blog content API
