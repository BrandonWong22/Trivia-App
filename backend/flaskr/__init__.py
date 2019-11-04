import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import math
import json

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection): 
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/categories')
  def get_categories(): 
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    categories = Category.query.all()
   
    if len(categories) == 0:
      abort(404)

    formatted_categories = {category.id: category.type for category in categories}

    return jsonify({
      'success': True,
      'categories': formatted_categories,
      'total_categories': len(Category.query.all())})

  @app.route('/questions')
  def get_questions():
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
  
    # try:
    selection = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, selection)
    categories = {category.id: category.type for category in Category.query.all()}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True, 
      'questions': current_questions,
      'total_questions': len(Question.query.all()), 
      'categories': [], 
      'current_category': None
    })

    # except: 
    #   abort(404)


  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    try: 
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None: 
        abort(404)

      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True, 
        #'deleted': question_id, 
        'questions': current_questions, 
        'total_questions': len(Question.query.all())
      })

    except: 
      abort(422)
  
  @app.route('/questions', methods=['POST'])
  def create_questions():
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_cateogry = body.get('category', None)
    new_difficulty_score = body.get('new_difficulty_score', None)

    try:
      question = Question(question=new_question, answer=new_answer, category=new_cateogry, difficulty=new_difficulty_score)
      question.insert()

      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True, 
        'created': question.id, 
        'questions': current_questions, 
        'total_questions': len(Question.query.all())
      })

    except: 
      abort(422)

  @app.route('/searchQuestions', methods=['POST'])
  def search_questions():
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    try:
      body = request.get_json()

      search = body.get('searchTerm', None)
      selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True, 
        'questions': current_questions, 
        'total_questions': len(Question.query.all())
      })

    except: 
      abort(405)


  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_categories(category_id):
    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    try:
      search_category = Category.query.filter(Category.id==category_id).one_or_none()

      selection = Question.query.filter(Question.category==category_id).all()
      current_questions = paginate_questions(request, selection)

      return jsonify({
        'success': True, 
        'questions': current_questions, 
        'total_questions': len(Question.query.all()), 
        'search_category': search_category.format()
      })

    except:
      abort(422)

    def get_random_question(): 
      max_id = len(Question.query.all()) - 1
      random_id = random.randint(0, max_id)
      random_question = Question.query.get(random_id)

      if random_question is None:
        return get_random_question()

      return random_question.format


    def get_random_question_from_category(category, prv_questions): 
      questions_from_category = Question.query.filter_by(category==category['id']).all()
      formatted_questions = [question.format for question in questions_from_category]
      random_question_index = random.randint(0, (len(formatted_questions) - 1))
      random_question = formatted_questions[random_question_index]

      for question in prv_questions:
        if question == random_question['id']:
          return get_random_queston_by_category(category, prv_questions)
      return random_question
    
  @app.route('/quizzes', methods=['POST'])
  def get_questions_play_quiz():
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
    body = request.get_json()

    quiz_category = body.get('get_category', None)
    prv_questions = body.get('prv_questions', None)
    current_question = {}

    category_id = int(quiz_category['id'])

    if category_id > 0: #A category has been selected
      current_question = get_random_question_from_category(quiz_category, prv_questions)

    else: #ALL has been selected
      current_question = get_random_question()
      for question in prv_questions:
        if question == current_question['id']:
          return get_quiz_question()

    return jsonify({
      'success': True,
      'question': current_question
    })


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error): 
    return jsonify({
      'success': False, 
      'error': 404, 
      'message': 'resource not found'
    }), 404 

  @app.errorhandler(405)
  def not_found(error): 
    return jsonify({
      'success': False, 
      'error': 405, 
      'message': 'method not allowed'
    }), 405 

  @app.errorhandler(422)
  def unprocessable(error): 
    return jsonify({
      'success': False,
      'error': 422, 
      'message': 'unprocessable'
    }), 422
  
  return app

    