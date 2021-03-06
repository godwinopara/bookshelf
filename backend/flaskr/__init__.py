import json
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Book

BOOKS_PER_SHELF = 8


def paginated_books(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PATCH,POST,DELETE,OPTIONS,PUT"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    @app.route('/books')
    def get_books():
        # Set the default page the user will receive first
        selection = Book.query.order_by(Book.id).all()
        current_books = paginated_books(request, selection)

        if len(current_books) == 0:
            abort(404)
        else:
            return jsonify({
                "success": True,
                "books": current_books,
                "total_books": len(Book.query.all())
            })

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    @app.route('/books/<int:book_id>', methods=["PATCH"])
    def update_book(book_id):
        book = Book.query.filter(Book.id == book_id).one_or_none()

        try:
            body = request.get_json()
            if book is None:
                abort(400)

            if 'rating' in body:
                book.rating = int(body['rating'])

            book.update()

            return jsonify({
                "success": True,
                "id": book.id
            })
        except:
            abort(400)

    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'

    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.

    @app.route('/books/<int:book_id>', methods=["DELETE"])
    def delete_book(book_id):
        book = Book.query.get(book_id)

        if len(book) == 0:
            abort(404)

        book.delete()

        books = Book.query.all()
        formated_book = [book.format() for book in books]

        return jsonify({
            "success": True,
            "total_books": len(formated_book),
            "books": formated_book,
            "total_books": len(formated_book)
        })

    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route('/books', methods=["POST"])
    def add_book():
        body = request.get_json()

        title = body.get('title', None)
        author = body.get('author', None)
        rating = body.get('rating', None)
        search = body.get('search')

        try:
            if search:
                selection = Book.query.order_by(Book.id).filter(
                    Book.title.ilike(f'%{search}%'))

                current_books = paginated_books(request, selection)

                return jsonify({
                    "success": True,
                    "books": current_books,
                    "total_books": len(selection.all())
                })
            else:
                new_book = Book(title=title, author=author, rating=rating)

                new_book.insert()

                books = Book.query.order_by(Book.id).all()
                formated_books = [book.format() for book in books]

                return jsonify({
                    "success": True,
                    "created": new_book.id,
                    "books": formated_books,
                    "total_books": len(formated_books)
                })

        except:
            abort(405)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        })

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        })

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        })

    return app
