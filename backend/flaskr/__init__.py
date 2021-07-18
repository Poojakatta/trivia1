import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS,cross_origin
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={'/':{'origins':'*'}})



  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTION')
    return response

  ''' 
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    categories = Category.query.all()
    categories_all = {}
    for category in categories:
      categories_all[category.id] = category.type
    if (len(categories_all)==0):
      abort(404)
    return jsonify({
    'success': True,
    'categories': categories_all
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions', methods=['GET'])
  def get_questions():
    selected_page = request.args.get('page', 1, type=int)
    current_index = selected_page - 1
    selection = Question.query.order_by(Question.id).limit(QUESTIONS_PER_PAGE).offset(current_index * QUESTIONS_PER_PAGE).all()
    questions = [question.format for question in selection]

    if (len(questions) == 0):
      abort(404)

    categories = Category.query.all()
    categories_all = {}
    for category in categories:
      categories_all[category.id] = category.type
    
    
    return jsonify({
      'success': True,
      'questions':questions,
      'totalQuestions':len(selection),
      'categories': categories_all
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter_by(id=id).one_or_none()
    
    if question is None:
      abort(404)
    question.delete()  
    return jsonify({
      'success': True,
      'question-id': question.id
    })

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_new_question():
    body=request.get_json()

    if body.get('searchTerm'):
      question_search_term = body.get('searchTerm')
      selection = Question.query.filter(Question.question.ilike(f'%{question_search_term}%')).order_by(Question.id).all()

      questions = [question.format for question in selection]      
  
      if(len(questions)==0):
       abort(404)
      else:
       return jsonify({
        'success': True,
        'questions': questions
      })
    else:
      new_question = body.get('question',None)
      new_answer = body.get('answer',None)
      new_category = body.get('category',None)
      new_difficulty = body.get('difficulty',None)

      if ((new_question is None) or (new_answer is None)
      or (new_difficulty is None) or (new_category is None)):
        abort(422)
        
      try:
        question=Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        

        return jsonify({
         'success': True
        })
      except:
         abort(422)
  

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''



  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions',methods=['GET'])
  def get_category_questions(category_id):
    category = Category.query.filter_by(id=category_id).one_or_none()

    if (category is None):
      abort(400)

    selection = Question.query.filter_by(category=category.id).all()
    questions=paginate_questions(request,selection)
  # return the results
    return jsonify({
    'success': True,
    'questions': questions,
    'total_questions': len(selection),
    'current_category': category.type
    })





  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_random_quiz_question():
        
     body = request.get_json()

     previous = body.get('previous_questions')

     category = body.get('quiz_category')

  # abort 400 if category or previous questions isn't found
     if ((category is None) or (previous is None)):
      abort(400)

  # load questions all questions if "ALL" is selected
     if (category['id'] == 0):
      questions = Question.query.all()
     else:
      questions = Question.query.filter_by(category=category['id']).all()

     total = len(questions)

  # get a random question
     def get_random_question():
      return questions[random.randrange(0, len(questions), 1)]

  # check if question has already been used
     def check_if_used(question):
      used = False
      for q in previous:
        if (q == question.id):
          used = True

      return used

  # get random question
     question = get_random_question()

     while (check_if_used(question)):
       question = get_random_question()

     if (len(previous) == total):
      return jsonify({
        'success': True
      })

     return jsonify({
         'success': True,
         'question': question.format()
      })

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
   '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
       "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
        }), 400
 
  return app

    