from flask import Flask, render_template, request, redirect, url_for
import datetime
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

@app.route('/')
def home():
    # Load blog posts from JSON file
    try:
        response = requests.get("https://api.npoint.io/db4eaa79651d1ec3953e")
        blog_posts = response.json()
    except FileNotFoundError:
        blog_posts = []
    
    year = datetime.datetime.now().year
    name = request.args.get('name')
    if name:
        # If name is provided, redirect to the name route
        return redirect(f'/guess/{name}')
    return render_template('index.html',
                         posts=blog_posts, 
                         page_title="Unwind your soul",
                         page_subtitle="A Meditation content related platform",
                         year=year)

@app.route('/about')
def about():
    year = datetime.datetime.now().year
    return render_template('about.html', 
                         page_title="About Meditations",
                         page_subtitle="This is what we do.",
                         year=year)

def send_contact_email(name, email, phone, message):
    """Send contact form email to website owner"""
    # Email configuration
    sender_email = "israepersonaluseonly@gmail.com"  
    sender_password = "password"   
    receiver_email = "israeguennouni99@gmail.com" 
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New Contact Form Submission from {name}"
    
    # Email body
    body = f"""
    New contact form submission received!
    
    Name: {name}
    Email: {email}
    Phone: {phone}
    Message: {message}
    
    This email was sent from your website contact form.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def form_entry():
    """Handle form submission and return form data"""
    form_data = {
        'name': request.form['name'],
        'email': request.form['email'], 
        'phone': request.form['phone'], 
        'message': request.form['message']
    }
    
    # Send email notification
    email_sent = send_contact_email(
        form_data['name'],
        form_data['email'],
        form_data['phone'],
        form_data['message']
    )
    
    # Add email status to form data
    form_data['email_sent'] = email_sent
    
    return form_data

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form_data = {
        'name': None,
        'email': None, 
        'phone': None, 
        'message': None
    }
    submitted = False
    
    if request.method == 'POST':
        form_data = form_entry()
        submitted = True
    
    year = datetime.datetime.now().year
    return render_template('contact.html',
                         submitted=submitted,
                         page_title="Contact Me",
                         page_subtitle="Have questions? I have answers.",
                         year=year,
                         **form_data)

@app.route('/post/<int:id>')
def post(id):
    # Load blog posts from JSON file
    try:
        response = requests.get("https://api.npoint.io/db4eaa79651d1ec3953e")
        blog_posts = response.json()
    except FileNotFoundError:
        blog_posts = []
    #find the specific post by id
    blog = None
    for post in blog_posts:
         if post['id'] == id:
             blog = post
             break
    year = datetime.datetime.now().year
    if blog is None:
        return "Post not found", 404
    
    return render_template('post.html', 
                         page_title=blog['title'],
                         page_subtitle=blog['subtitle'],
                         page_meta="Posted by Meditations",
                         page_body=blog['body'],
                         year=year)

if __name__ == '__main__':
    app.run(debug=True) 