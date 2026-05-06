from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random, string
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:qwerty123@localhost/url_shortener')
db = SQLAlchemy(app)

class Url(db.Model):
   id = db.Column(db.Integer,primary_key = True)
   original_url = db.Column(db.String(500), nullable = False)
   short_code = db.Column(db.String(10), nullable = False)
   clicks = db.Column(db.Integer,default = 0)

with app.app_context():
   db.create_all()

def generate_short_code():
   chararcters = string.ascii_letters + string.digits
   return ''.join(random.choices(chararcters,k=8))

@app.route('/')
def home():
   return redirect(url_for('submit'))

@app.route('/submit', methods = ['GET','POST'])
def submit():
   total_urls = Url.query.count()
   if request.method == 'POST':
      url = request.form['url']
      if not url.startswith('http://') and not url.startswith('https://'):
         url = 'https://' + url
         
      short = generate_short_code()
      new = Url(original_url = url,short_code = short)
      db.session.add(new)
      db.session.commit()
      base_url = request.host_url.rstrip('/')
      short_url = f"{base_url}/{short}"
      return render_template('submit.html', short_code=short, short_url=short_url, total_urls=total_urls)
   return render_template('submit.html', total_urls=total_urls)
   
@app.route('/<short_code>') 
def redirect_url(short_code):
   url_entry = Url.query.filter_by(short_code=short_code).first()

   if url_entry is None:
      return 'URL not found',404
   
   url_entry.clicks += 1
   db.session.commit()
   return redirect(url_entry.original_url)

if __name__ == '__main__':
   app.run(debug=True)