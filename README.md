# Tutor Hunter

# Introduction
TutorHunter is a RESTful web application, integrating database storage (MySQL), a back-end API, and front-end. Tutor Hunter is a platform that connects users with tutors.
# Environment
* <b>OS</b>: UBUNTU 16.04
* <b>Language</b>: Python 3.6
* <b>Web server</b>: nginx/1.10.3
* <b>Application Server</b>: Flask 2.0.2, Jinja 3.0.2
* <b>Web Server Gateway</b>: gunicorn(version 20.1.0)
* <b>Database</b>: MySQL ver 14.14 Distrib 5.7.33
* <b>Style</b>
   <ul><li><b>Python</b>: PEP 8</li>
  </ul>
* <b>Packages Required</b>
  <ul><li><b>PILLIOW</b>: is Python Imaging Library which provides extensive file format support, an efficient internal representation, and fairly powerful image processing capabilities.</li>
  <li><b>bcrypt</b>: Python package used for password hashing</li>
  <li><b>SQLAlchemy</b>: Object Relational Mapper</li>
  </ul>
# Static
The front-end of TutorHunter was designed using HTML/CSS pages integrated using Flask. In addition, Bootsrap is also used to facilitate the design and implementation process.
# Classes
TutorHunter supports the following classes:
* User
* Tutor
* Parent_requests

![Architecture](architecture.png)

# Environment Variables
MAIL_USERNAME and MAIL_PASSWORD are environment variables that should be set since they are used in the application for emailing functionality.
# Authors
+ Abebayehu: <absa3852@gmail.com> 
+ Yosef: <Yosefsamuel22@gmail.com>
