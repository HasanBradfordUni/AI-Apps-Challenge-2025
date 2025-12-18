from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import sys

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-for-ai-chatbot'
    
    # Import and register December chatbot routes
    try:
        from routes import register_routes as register_december_routes
        register_december_routes(app)
        print("December AI Chatbot routes registered successfully")
    except ImportError as e:
        print(f"Warning: Could not import December chatbot routes: {e}")
    
    @app.route('/')
    def index():
        return redirect(url_for('chatbot_home'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=6922, debug=True)