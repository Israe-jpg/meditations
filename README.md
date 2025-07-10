# meditations

Flask application built with flask and the Clean Blog template provided by boostrap.

**#features**
**Displaying well being related content ( meditatiosn and exercise) in the form of posts with dynamic content loading.
**Mobile friendly design due to boostrap design
**Contact form made with "SMTP" with email notifications of the information provided by users
**Blog posts loaded with external api, created with "npoint.io"
**Clean and minimalistic design suited for the main theme of the website

**#prerequisites**
**Python 3.7 or higher
pip
Git

**#Installations**
**Create a virtual environment**
"python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
 **Install dependencies**
pip install -r requirements.txt"

**project structure**
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

**#Acknowledgments**
-Bootstrap Clean Blog Theme=(https://startbootstrap.com/theme/clean-blog) for the beautiful design
-Flask = (https://flask.palletsprojects.com/) for the web framework
-npoint.io = (https://npoint.io/) for the blog content API       
