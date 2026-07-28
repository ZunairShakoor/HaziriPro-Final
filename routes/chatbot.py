from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from services.chatbot_service import ChatbotService
from models.employee import Employee

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/')
@login_required
def index():
    return render_template('chatbot/chatbot.html')

@chatbot_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        message = request.json.get('message', '')

        # Prefer the employee actually linked to the logged-in account
        # (the normal case for a regular employee using the assistant).
        employee = Employee.query.filter_by(user_id=current_user.id).first()
        employee_id = employee.employee_id if employee else None

        # If this account has no linked employee (e.g. an admin/HR login),
        # fall back to whatever employee ID was resolved earlier in this
        # browser session — this is what lets the bot "remember" an ID
        # someone typed in a previous message instead of asking again
        # on every single message.
        if not employee_id:
            employee_id = session.get('chatbot_employee_id')

        chatbot = ChatbotService(employee_id)
        response = chatbot.process_query(message)

        # If the chatbot just resolved a new ID from the message itself,
        # remember it for the rest of this session.
        if chatbot.employee_id and not employee_id:
            session['chatbot_employee_id'] = chatbot.employee_id
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'response': f'Error: {str(e)}'
        })