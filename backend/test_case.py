import unittest
import json
from flaskr import create_app
from models import setup_db


class Bookshelf(unittest.TestCase):
    def setUp(self) -> None:
        # define test variables and initialize app
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

    def tearDown(self) -> None:
        # Executed after each test
        pass

    def test_get_books(self):
        # Test ____________________
        res = self.client().get('/books')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assetEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertTrue(data['books'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000', json={'rating': 1})
        data = json.loads(res.data)

        self.assetEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['total_books'])
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))


if __name__ == "__main__":
    unittest.main()
