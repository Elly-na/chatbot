import re
from fuzzywuzzy import fuzz
from training_data import TRAINING_PATTERNS

class SmartChatbot:
    def __init__(self):
        self.device_config = {
            "hostname": "Router1",
            "ip_address": "Not configured",
            "interface": "GigabitEthernet0/0",
            "status": "down"
        }
        self.confidence_threshold = 70  # Minimum match confidence
    
    def extract_parameters(self, user_input, pattern):
        """Extract parameters like IP addresses or names from user input"""
        # Extract IP address
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', user_input)
        
        # Extract hostname (word after 'to' or last word)
        name_match = re.search(r'(?:to|as|it)\s+(\w+)', user_input)
        if not name_match:
            words = user_input.split()
            if len(words) > 2:
                name_match = words[-1]
        
        params = {}
        if ip_match:
            params['ip'] = ip_match.group(1)
        if name_match:
            params['name'] = name_match if isinstance(name_match, str) else name_match.group(1)
        
        return params
    
    def find_best_match(self, user_input):
        """Find the best matching intent using fuzzy matching"""
        user_input = user_input.lower().strip()
        best_match = None
        best_score = 0
        best_intent = None
        
        for intent, data in TRAINING_PATTERNS.items():
            for pattern in data['patterns']:
                # Calculate similarity score
                score = fuzz.ratio(user_input, pattern)
                
                # Also check if key words match
                partial_score = fuzz.partial_ratio(user_input, pattern)
                
                # Take the better score
                final_score = max(score, partial_score)
                
                if final_score > best_score:
                    best_score = final_score
                    best_match = pattern
                    best_intent = intent
        
        # Return match if confidence is above threshold
        if best_score >= self.confidence_threshold:
            return best_intent, best_score
        
        return None, 0
    
    def generate_response(self, intent, params):
        """Generate appropriate response based on intent"""
        
        if intent == 'show_device':
            return TRAINING_PATTERNS[intent]['response_template'].format(
                hostname=self.device_config['hostname'],
                interface=self.device_config['interface'],
                status=self.device_config['status']
            )
        
        elif intent == 'show_ip':
            return TRAINING_PATTERNS[intent]['response_template'].format(
                ip_address=self.device_config['ip_address'],
                interface=self.device_config['interface'],
                status=self.device_config['status']
            )
        
        elif intent == 'configure_ip':
            if 'ip' in params:
                self.device_config['ip_address'] = params['ip']
                return TRAINING_PATTERNS[intent]['response_template'].format(
                    ip=params['ip']
                )
            return "Please provide a valid IP address (e.g., 192.168.1.1)"
        
        elif intent == 'set_hostname':
            if 'name' in params:
                self.device_config['hostname'] = params['name']
                return TRAINING_PATTERNS[intent]['response_template'].format(
                    name=params['name']
                )
            return "Please provide a hostname"
        
        elif intent == 'enable_interface':
            self.device_config['status'] = "up"
            return TRAINING_PATTERNS[intent]['response_template'].format(
                interface=self.device_config['interface']
            )
        
        elif intent == 'disable_interface':
            self.device_config['status'] = "down"
            return TRAINING_PATTERNS[intent]['response_template'].format(
                interface=self.device_config['interface']
            )
        
        elif intent == 'show_config':
            config = f"""{'='*40}
hostname {self.device_config['hostname']}
!
interface {self.device_config['interface']}
  ip address {self.device_config['ip_address']}
  status {self.device_config['status']}
{'='*40}"""
            return TRAINING_PATTERNS[intent]['response_template'].format(
                config=config
            )
        
        elif intent == 'greeting':
            return TRAINING_PATTERNS[intent]['response_template']
        
        elif intent == 'help':
            return TRAINING_PATTERNS[intent]['response_template']
        
        return "I didn't understand that. Try rephrasing or type 'help'"
    
    def chat(self, user_input):
        """Main chat function"""
        # Find best matching intent
        intent, confidence = self.find_best_match(user_input)
        
        if intent:
            # Extract parameters from input
            params = self.extract_parameters(user_input, intent)
            
            # Generate response
            response = self.generate_response(intent, params)
            
            # Add confidence indicator for testing
            if confidence < 85:
                response += f"\n(Confidence: {confidence}%)"
            
            return response
        else:
            return "I'm not sure what you mean. Type 'help' to see available commands."


def main():
    bot = SmartChatbot()
    
    print("="*60)
    print("  SMART NETWORK CONFIGURATION ASSISTANT")
    print("  (with Natural Language Understanding)")
    print("="*60)
    print("\nTry natural commands like:")
    print("  • 'what is my device info'")
    print("  • 'please show me the ip'")
    print("  • 'can you set ip to 192.168.1.100'")
    print("  • 'change the hostname to CoreRouter'")
    print("\nType 'exit' to quit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nBot: Goodbye! Configuration saved.\n")
            break
        
        response = bot.chat(user_input)
        print(f"\nBot: {response}\n")


if __name__ == "__main__":
    main()