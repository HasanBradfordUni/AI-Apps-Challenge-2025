class PromptModeManager:
    """Manages different prompt modes for the chatbot"""
    
    def __init__(self):
        self.modes = {
            'general': {
                'name': 'General Assistant',
                'description': 'General purpose AI assistant',
                'system_prompt': 'You are a helpful AI assistant. Provide clear, concise, and helpful responses.',
                'icon': '🤖'
            },
            'code': {
                'name': 'Code Assistant',
                'description': 'Programming and development help',
                'system_prompt': 'You are a programming assistant. Help with code, debugging, best practices, and technical questions.',
                'icon': '💻'
            },
            'writing': {
                'name': 'Writing Assistant',
                'description': 'Content writing and editing',
                'system_prompt': 'You are a writing assistant. Help with content creation, editing, grammar, and writing improvement.',
                'icon': '✍️'
            },
            'qa': {
                'name': 'Q&A Mode',
                'description': 'Question and answer format',
                'system_prompt': 'Answer questions directly and factually. Provide sources when possible.',
                'icon': '❓'
            },
            'creative': {
                'name': 'Creative Mode',
                'description': 'Creative writing and brainstorming',
                'system_prompt': 'You are a creative assistant. Help with brainstorming, creative writing, and innovative ideas.',
                'icon': '🎨'
            },
            'analysis': {
                'name': 'Analysis Mode',
                'description': 'Data analysis and insights',
                'system_prompt': 'You are an analytical assistant. Focus on data analysis, insights, and logical reasoning.',
                'icon': '📊'
            }
        }
    
    def get_modes(self):
        """Get all available prompt modes"""
        return self.modes
    
    def get_mode(self, mode_id):
        """Get specific prompt mode"""
        return self.modes.get(mode_id, self.modes['general'])
    
    def get_system_prompt(self, mode_id):
        """Get system prompt for mode"""
        mode = self.get_mode(mode_id)
        return mode['system_prompt']