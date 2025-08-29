# Meditations

Flask application built with Flask and the Clean Blog template provided by Bootstrap.

## Features

- **Displaying well-being related content** (meditations and exercise) in the form of posts with dynamic content loading
- **Mobile friendly design** due to Bootstrap design
- **Contact form** made with SMTP with email notifications of the information provided by users
- **Blog posts loaded** with external API, created with npoint.io
- **Clean and minimalistic design** suited for the main theme of the website
- **User Authentication** with login/register functionality
- **Dynamic PDF Generation** - Personalized ID cards for logged-in users
- **Rich Text Editor** - CKEditor integration for creating formatted blog posts
- **Role-based Access Control** - Admin users can create, edit, and delete posts
- **Secure Password Management** - Hashed passwords using Werkzeug security
- **SQLite Database** - Persistent storage for users, posts, and comments
- **Comment System** - Users can comment on blog posts with authentication
- **Form Validation** - Server-side validation using WTForms
- **Session Management** - Secure user sessions with Flask-Login
- **Responsive Bootstrap UI** - Professional, mobile-first design
- **Email Integration** - SMTP contact form with email notifications
- **Profile Management** - User profile pages with customization options
- **Search Functionality** - AJAX-powered search suggestions for posts

### Key Dependencies & Technologies

- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM for post and user management
- **Flask-Login** - User authentication and session management
- **Flask-WTF & WTForms** - Form handling and validation
- **Flask-CKEditor** - Rich text editor for blog posts
- **Flask-Bootstrap4** - Bootstrap integration
- **pdfkit** - HTML to PDF conversion (for ID card downloads)
- **wkhtmltopdf** - PDF generation engine
- **Werkzeug** - Password hashing and security
- **SQLite** - Database engine
- **Bootstrap** - Frontend CSS framework
- **SMTP (smtplib)** - Email functionality for contact form

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

3. **Install wkhtmltopdf (Required for PDF generation)**

   #### Windows

   1. Download from: https://wkhtmltopdf.org/downloads.html
   2. Install to default location or note custom path
   3. Update the path in `server.py` if needed:

   ```python
   config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe')
   ```

   #### Linux/Ubuntu

   ```bash
   sudo apt-get install wkhtmltopdf
   ```

   #### macOS

   ```bash
   brew install wkhtmltopdf
   ```

4. **Start the development server**

   ```bash
   python server.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## PDF Download Feature

### Overview

The application includes a dynamic PDF generation feature that creates personalized ID cards for logged-in users. When users log in, they see a popup with a download button that generates a custom PDF containing their personal information.

### How It Works

1. **User Login**: When a user successfully logs in, a popup appears on the home page
2. **PDF Generation**: Clicking "Download Your File" triggers the `/download` route
3. **Dynamic Content**: The PDF is generated in real-time using the user's data:
   - User's name
   - Email address
   - Current date
   - Membership status

### Technical Implementation

#### Backend (Flask)

- **Route**: `/download` (requires authentication)
- **Template**: `pdf_template.html` - HTML template for PDF content
- **Library**: `pdfkit` - Converts HTML to PDF
- **Data**: User information from `current_user` object

#### Frontend

- **Popup Modal**: Bootstrap modal that appears for logged-in users only
- **Download Button**: Makes GET request to `/download` route
- **File Delivery**: PDF downloads with filename format: `{username}_id_card.pdf`

### Customization

- Modify `pdf_template.html` to change PDF layout and content
- Update popup styling in `index.html`
- Adjust PDF filename format in the download route
- Add more user data fields as needed

### Security Note

The download route is protected with `@login_required` decorator, ensuring only authenticated users can generate and download their personal PDF documents.

## Project Structure

```
meditations/
├── server.py              # Main application with routes
├── requirements.txt       # Python dependencies
├── instance/
│   └── blog.db           # SQLite database
├── static/
│   ├── styles.css        # Custom styles
│   ├── script.js         # JavaScript functionality
│   ├── background.jpg    # Background images
│   └── files/            # Static files for download
├── templates/
│   ├── index.html        # Home page with popup modal
│   ├── about.html        # About page
│   ├── contact.html      # Contact form
│   ├── post.html         # Individual blog post
│   ├── login.html        # User login
│   ├── register.html     # User registration
│   ├── pdf_template.html # PDF generation template
│   ├── header.html       # Navigation header
│   └── base.html         # Base template
└── data/
    └── blog-data.txt     # Blog content data
```

## Troubleshooting

### PDF Generation Issues

1. **"No wkhtmltopdf executable found"**

   - Ensure wkhtmltopdf is properly installed
   - Check and update the path in the configuration
   - Verify the executable exists at the specified location

2. **Path Issues**
   - Use `where wkhtmltopdf` (Windows) or `which wkhtmltopdf` (Linux/Mac) to find the correct path
   - Update the configuration in `server.py` with the correct path

### General Issues

1. **Database Errors**

   - Delete the `instance/blog.db` file and restart the application to recreate the database

2. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Activate your virtual environment before running the application

## Usage

1. **Register** a new account or **Login** with existing credentials
2. **Browse** meditation posts on the home page
3. **Create** new blog posts (when logged in)
4. **Download** your personalized ID card via the popup (when logged in)
5. **Contact** the site owner through the contact form

## Acknowledgments

- [Bootstrap Clean Blog Theme](https://startbootstrap.com/theme/clean-blog) for the beautiful design
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [npoint.io](https://npoint.io/) for the blog content API
- [wkhtmltopdf](https://wkhtmltopdf.org/) for PDF generation
