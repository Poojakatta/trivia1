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
        self.database_name = "trivia"
        self.database_path = "postgresql://pooja:1234@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Capital City of Telangana?',
            'answer': 'Hyderabad',
            'difficulty': 1,
            'category': '3'
        }

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
    def test_get_questions(self):
 
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    def test_404_get_questions(self):

        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_delete_question(self):

        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()

        id = question.id
        questions_before_delete = Question.query.all()
        response = self.client().delete('/questions/{}'.format(id))
        data = json.loads(response.data)

        questions_after_delete = Question.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check if one less question after delete
        self.assertTrue(len(questions_before_delete) - len(questions_after_delete) == 1)

    def test_create_new_question(self):
        
        questions_before_creation = Question.query.all()

        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        questions_after_creation = Question.query.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(len(questions_after_creation) - len(questions_before_creation) == 1)

    def test_422_if_question_creation_fails(self):

        questions_before_creation = Question.query.all()

        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        questions_after_creation = Question.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        self.assertTrue(len(questions_after_creation) == len(questions_before_creation))

    def test_searchterm_in_questions(self):

        response = self.client().post('/questions',json={'searchTerm': 'Andhra'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_404_if_searchterm_questions_fails(self):
    
        response = self.client().post('/questions',json={'searchTerm': 'pooja'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_questions_by_category(self):
        self.client().post('/questions', json=self.new_question)        
        response = self.client().get('/categories/3/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Geography')

    def test_400_if_questions_by_category_fails(self):

        response = self.client().get('/categories/7/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_play_quiz_game(self):

        response = self.client().post('/quizzes',json={'previous_questions': [20, 21],
                                            'quiz_category': {'type': 'Geography', 'id': '1'}})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)
        self.assertNotEqual(data['question']['id'], 20)
        self.assertNotEqual(data['question']['id'], 21)

    def test_play_quiz_fails(self):
    
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


if __name__ == "__main__":
    unittest.main()