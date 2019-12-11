import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # TEST GET METHOD ON CATEGORIES
    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data["categories"]), 6)

    # TEST GET METHOD ON QUESTIONS
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]), 19)

    # TEST 404 ERROR ON QUESTIONS
    def test_404_if_questions_does_not_exist(self):
        res = self.client().get('/questions?page=100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # TEST 404 ERROR ON DELETING QUESTIONS
    def test_404_delete(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # TEST POST METHOD ON QUESTIONS
    def test_post_question(self):
        total_questions_before_post = len(Question.query.all())
        post_question = {
            'question': "Test Question",
            "answer": "Test Answer",
            "difficulty": 1,
            'category': 1
        }

        res = self.client().post('/questions', json=post_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(
            data['total_questions'],
            total_questions_before_post + 1)

    # TEST 405 ERROR ON POST QUESTIONS METHOD
    def test_405_post_questions(self):
        post_question = {
            'question': "Test Question",
            "answer": "Test Answer",
            "difficulty": 1,
            'category': 1
        }

        res = self.client().post('/questions/1000', json=post_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    # TEST SEARCH QUESTIONS METHOD
    def test_search_question(self):
        post_data = {
            'searchTerm': 'title',
        }
        res = self.client().post('/searchQuestions', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_get_question_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data['search_category']['id'], 1)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], len(Question.query.all()))

    # TEST 422 INVALID SEARCH METHOD
    def test_422_search_invalid_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data['message'], 'unprocessable')

    # TEST PLAY QUIZ
    def test_post_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 1
            }
        }
        res = self.client().post('/quizzes', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    # TEST 404 ERROR PLAY QUIZ
    def test_404_post_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Fail',
                'id': 9
            }
        }
        res = self.client().post('/quizzes', json=post_data)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
