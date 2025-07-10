from flask import Flask, render_template, request
import datetime
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MYSECRETKEY1234'

#Creating a flask form
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])

#get current year
def get_current_year():
    return datetime.datetime.now().year

#fetch blog posts from created api
def get_blog_posts():
    try:
        response = requests.get("https://api.npoint.io/db4eaa79651d1ec3953e")
        response.raise_for_status()
        blog_posts = response.json()
    except (requests.RequestException, requests.HTTPError, ValueError, FileNotFoundError):
        #network errors, HTTP status errors, JSON parsing errors,and file errors
        blog_posts = []
    return blog_posts

@app.route('/')
def home():
    return render_template('index.html',
                         posts=get_blog_posts(), 
                         page_title="Unwind your soul",
                         page_subtitle="A Meditation content related platform",
                         year=get_current_year())

@app.route('/about')
def about():
    return render_template('about.html', 
                         page_title="About Meditations",
                         page_subtitle="This is what we do.",
                         year=get_current_year())

# def send_contact_email(name, email, phone, message):

#     # Email configuration
#     sender_email = "israepersonaluseonly@gmail.com"  
#     sender_password = "password"   
#     receiver_email = "israeguennouni99@gmail.com" 
    
#     # Create message
#     msg = MIMEMultipart()
#     msg['From'] = sender_email
#     msg['To'] = receiver_email
#     msg['Subject'] = f"New Contact Form Submission from {name}"
    
#     # Email body
#     body = f"""
#     New contact form submission received!
    
#     Name: {name}
#     Email: {email}
#     Phone: {phone}
#     Message: {message}
    
#     This email was sent from your website contact form.
#     """
    
#     msg.attach(MIMEText(body, 'plain'))
    
#     try:
#         # Create SMTP session
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(sender_email, sender_password)
        
#         # Send email
#         text = msg.as_string()
#         server.sendmail(sender_email, receiver_email, text)
#         server.quit()
        
#         return True
#     except Exception as e:
#         print(f"Email sending failed: {e}")
#         return False

# def form_entry():
#     form_data = {
#         'name': request.form['name'],
#         'email': request.form['email'], 
#         'phone': request.form['phone'], 
#         'message': request.form['message']
#     }
    
#     # Send email notification
#     email_sent = send_contact_email(
#         form_data['name'],
#         form_data['email'],
#         form_data['phone'],
#         form_data['message']
#     )
    
#     # Add email status to form data
#     form_data['email_sent'] = email_sent
    
#     return form_data

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    submitted = False
    
    if form.validate_on_submit():
        form_data = form
        submitted = True
    
    return render_template('contact.html',
                         submitted=submitted,
                         page_title="Contact Me",
                         page_subtitle="Have questions? I have answers.",
                         year=get_current_year(),
                         form = form)

@app.route('/post/<int:id>')
def post(id):
    #get blogs first
    blog_posts = get_blog_posts()
    #find the specific post by id
    blog = None
    for post in blog_posts:
         if post['id'] == id:
             blog = post
             break
    if blog is None:
        return "Post not found", 404
    
    return render_template('post.html', 
                         page_title=blog['title'],
                         page_subtitle=blog['subtitle'],
                         page_meta="Posted by Meditations",
                         page_body=blog['body'],
                         year=get_current_year())

if __name__ == '__main__':
    app.run(debug=True) 