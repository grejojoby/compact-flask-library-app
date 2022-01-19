
from flask import Flask, render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy import update
import requests
import json

from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Books(db.Model):
    __tablename__ = 'books'
    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    authors = db.Column(db.String(255), nullable=False)
    stockQty = db.Column(db.Integer, nullable=False, default=0)
    timesIssued = db.Column(db.Integer, nullable=False, default=0)
    
    def __repr__(self):
        return 'Book'+str(self.book_id)

@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    
    most_popular=Books.query.order_by(Books.timesIssued.desc()).limit(5).all()
    least_stock=Books.query.order_by(Books.stockQty).limit(5).all()
    sum = Books.query.with_entities(func.sum(Books.stockQty).label('total')).first().total
    total_titles=Books.query.count()

    return render_template('index.html',most_popular=most_popular,total_books=sum, least_stock=least_stock,total_titles=total_titles)


@app.route('/books')
def books():
    all_books=Books.query.all()
    return render_template('books.html', all_books=all_books)

@app.route('/add_books', methods=['GET', 'POST'])
def add_books():
    if request.method=='POST':
        book_id=int(request.form['book_id'])
        book_title=request.form['title']
        book_author=request.form['author']
        book_stockQty=request.form['stockQty']
        new_book =Books(title=book_title,authors=book_author,stockQty=book_stockQty,timesIssued=0)
        db.session.add(new_book)
        db.session.commit()
        return redirect('/books')

    else:
        return render_template('add_books.html')

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def update_book(id):
    book = Books.query.filter_by(book_id=id).first()
    if request.method=='POST':
        title=request.form['title']
        authors=request.form['authors']
        stockQty=request.form['stockQty']
        book.title = title
        book.authors = authors
        book.stockQty = stockQty
        db.session.commit()
        return redirect('/books')
    else:
        return render_template('edit_book.html',book=book)
    
@app.route('/books/delete/<int:id>')
def delete_book(id):
    book=Books.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/books')

@app.route('/books/import/<int:id>', methods=['GET', 'POST'])
def import_book(id):
    r = requests.get('https://frappe.io/api/method/frappe-library?isbn='+str(id))
    book_details = json.loads(r.text)['message'][0]
    book_title=book_details["title"]
    book_author=book_details["authors"]
    book_stockQty=request.form['qty']
    new_book =Books(title=book_title,authors=book_author,stockQty=book_stockQty,timesIssued=0)
    db.session.add(new_book)
    db.session.commit()
    return redirect('/books')


if __name__ == '__main__':
    app.run(debug=True)
    