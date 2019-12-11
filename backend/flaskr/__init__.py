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

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Get categories endpoint
    @app.route('/categories')
    def get_categories():
    
        categories = Category.query.all()

        if len(categories) == 0:
            abort(404)

        formatted_categories = {
            category.id: category.type for category in categories}

        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'total_categories': len(Category.query.all())})

    # Get questions endpoint
    @app.route('/questions')
    def get_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)
        categories = {
            category.id: category.type for category in Category.query.all()}

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories,
        })

    # Delete question endpoint
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):

        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            abort(422)

    # Post question endpoint
    @app.route('/questions', methods=['POST'])
    def create_questions():

        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_cateogry = body.get('category', None)
        new_difficulty_score = body.get('new_difficulty_score', None)

        try:
            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_cateogry,
                difficulty=new_difficulty_score)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            abort(422)

    # Post question endpoint
    @app.route('/searchQuestions', methods=['POST'])
    def search_questions():

        try:
            body = request.get_json()

            search = body.get('searchTerm', None)
            selection = Question.query.order_by(
                Question.id).filter(
                Question.question.ilike(
                    '%{}%'.format(search)))
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except BaseException:
            abort(405)

    # Get unique quetion endpioint
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_categories(category_id):

        try:
            search_category = Category.query.filter(
                Category.id == category_id).one_or_none()

            selection = Question.query.filter(
                Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'search_category': search_category.format()
            })

        except BaseException:
            abort(422)

    # Get randon question
    def get_random_question():
        max_id = len(Question.query.all()) - 1
        random_id = random.randint(0, max_id)
        random_question = Question.query.get(random_id)

        if random_question is None:
            return get_random_question()

        return random_question.format()

    # Get randon question based on category
    def get_random_question_from_category(category, previous_questions):
        questions_from_category = Question.query.filter_by(
            category=category['id']).all()
        formatted_questions = [question.format()
                               for question in questions_from_category]
        random_question_index = random.randint(
            0, (len(formatted_questions) - 1))
        random_question = formatted_questions[random_question_index]

        for question in previous_questions:
            if question == random_question['id']:
                return get_random_question_from_category(
                    category, previous_questions)
        return random_question

    # Post quiz endpoint
    @app.route('/quizzes', methods=['POST'])
    def get_questions_play_quiz():

        body = request.get_json()

        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)
        current_question = {}

        category_id = int(quiz_category['id'])

        try:
            if category_id > 0:  # A category has been selected
                current_question = get_random_question_from_category(
                    quiz_category, previous_questions)

            else:  # ALL has been selected
                current_question = get_random_question()
                for question in previous_questions:
                    if question == current_question['id']:
                        return get_random_question()

            return jsonify({
                'success': True,
                'question': current_question
            })

        except BaseException:
            abort(404)

    #Error Handlers
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
