from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from database import ChatDatabase
from cisco_commands import DEVICE_CONFIGS, COMMAND_CATEGORIES, HELP_TEXT
from fuzzywuzzy import fuzz
import re
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Initialize database
db = ChatDatabase()

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists
        user_id = db.verify_user(username, password)
        if user_id:
            # User exists and password is correct
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('home'))
        else:
            # User does not exist, create a new user
            new_user_id = db.create_user(username, password)
            if new_user_id:
                session['user_id'] = new_user_id
                session['username'] = username
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Username already exists or invalid input')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    """Main chatbot page"""
    return render_template('index.html', username=session.get('username'))

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        message = data.get('message', '')
        chat_id = data.get('chat_id')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process command
        result = process_command(message)
        
        # Save messages to database
        if chat_id:
            db.add_message(chat_id, 'user', message)
            db.add_message(
                chat_id, 
                'bot', 
                result['text'], 
                result.get('commands'), 
                result.get('explanation')
            )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chats', methods=['GET'])
@login_required
def get_chats():
    """Get user's chats"""
    user_id = session.get('user_id')
    chats = db.get_user_chats(user_id)
    return jsonify(chats)

@app.route('/api/chats', methods=['POST'])
@login_required
def create_chat():
    """Create new chat"""
    user_id = session.get('user_id')
    data = request.json
    name = data.get('name', 'New Chat')
    
    chat_id = db.create_chat(user_id, name)
    return jsonify({'id': chat_id, 'name': name})

@app.route('/api/chats/<int:chat_id>', methods=['GET'])
@login_required
def get_chat_messages(chat_id):
    """Get messages in a chat"""
    messages = db.get_chat_messages(chat_id)
    return jsonify(messages)

@app.route('/api/chats/<int:chat_id>', methods=['PUT'])
@login_required
def rename_chat(chat_id):
    """Rename a chat"""
    data = request.json
    new_name = data.get('name')
    
    if new_name:
        db.rename_chat(chat_id, new_name)
        return jsonify({'success': True})
    
    return jsonify({'error': 'No name provided'}), 400

@app.route('/api/chats/<int:chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    """Delete a chat"""
    db.delete_chat(chat_id)
    return jsonify({'success': True})

def process_command(user_input):
    """Process user command with fuzzy matching and typo tolerance"""
    input_lower = user_input.lower().strip()
    
    # Normalize common typos
    input_lower = normalize_typos(input_lower)
    
    # Help commands
    if 'help' in input_lower:
        category = extract_help_category(input_lower)
        if category and category in HELP_TEXT:
            return {
                'type': 'bot',
                'text': HELP_TEXT[category],
                'commands': None,
                'explanation': f'Help for {category} commands'
            }
        else:
            return {
                'type': 'bot',
                'text': HELP_TEXT['all'],
                'commands': None,
                'explanation': 'All available commands'
            }
    
    # Show device configuration
    device_match = re.search(r'(?:show|display|get).*(?:commands?|config).*(?:for|of)?\s*(r[12]|s[12])', input_lower)
    if device_match:
        device = device_match.group(1).upper()
        if device in DEVICE_CONFIGS:
            config = DEVICE_CONFIGS[device]
            return {
                'type': 'bot',
                'text': f'Complete configuration for {device}',
                'commands': config['full_config'],
                'explanation': f'This is the full Cisco IOS configuration for {device}'
            }
    
    # RIP configuration
    if 'rip' in input_lower:
        device_match = re.search(r'(?:for|on)\s*(r[12])', input_lower)
        if device_match:
            device = device_match.group(1).upper()
            if device in DEVICE_CONFIGS and 'rip_config' in DEVICE_CONFIGS[device]:
                return {
                    'type': 'bot',
                    'text': f'RIP routing configuration for {device}',
                    'commands': DEVICE_CONFIGS[device]['rip_config'],
                    'explanation': f'This configures RIPv2 on {device}'
                }
    
    # Set hostname
    hostname_match = re.search(r'(?:set|change|configure).*hostname.*(?:to|as)?\s*([a-z0-9]+)', input_lower)
    if hostname_match:
        hostname = hostname_match.group(1).upper()
        return {
            'type': 'bot',
            'text': f'Setting hostname to {hostname}',
            'commands': f'''enable
configure terminal
hostname {hostname}
exit''',
            'explanation': f'This sets the device hostname to {hostname}'
        }
    
    # Configure IP address
    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_lower)
    interface_match = re.search(r'(?:on|interface|int)\s*([a-z0-9\/]+)', input_lower)
    
    if ip_match and interface_match and ('ip' in input_lower or 'configure' in input_lower):
        ip = ip_match.group(1)
        interface = interface_match.group(1)
        mask_match = re.search(r'mask\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_lower)
        mask = mask_match.group(1) if mask_match else '255.255.255.0'
        
        return {
            'type': 'bot',
            'text': f'Configuring IP {ip} on {interface}',
            'commands': f'''enable
configure terminal
interface {interface}
ip address {ip} {mask}
no shutdown
exit''',
            'explanation': f'This assigns IP {ip}/{mask} to interface {interface}'
        }
    
    # Enable interface
    if ('enable' in input_lower or 'turn on' in input_lower or 'no shut' in input_lower) and 'interface' in input_lower:
        interface_match = re.search(r'(?:interface|int)\s*([a-z0-9\/]+)', input_lower)
        if interface_match:
            interface = interface_match.group(1)
            return {
                'type': 'bot',
                'text': f'Enabling interface {interface}',
                'commands': f'''enable
configure terminal
interface {interface}
no shutdown
exit''',
                'explanation': f'This brings up interface {interface}'
            }
    
    # Disable interface
    if ('disable' in input_lower or 'shut down' in input_lower or 'shutdown' in input_lower) and 'interface' in input_lower:
        interface_match = re.search(r'(?:interface|int)\s*([a-z0-9\/]+)', input_lower)
        if interface_match:
            interface = interface_match.group(1)
            return {
                'type': 'bot',
                'text': f'Disabling interface {interface}',
                'commands': f'''enable
configure terminal
interface {interface}
shutdown
exit''',
                'explanation': f'This shuts down interface {interface}'
            }
    
    # Switchport configuration
    if 'switchport' in input_lower:
        interface_match = re.search(r'(?:on|interface|int)\s*([a-z0-9\/]+)', input_lower)
        mode_match = re.search(r'mode\s*(access|trunk)', input_lower)
        
        if interface_match:
            interface = interface_match.group(1)
            mode = mode_match.group(1) if mode_match else 'access'
            
            return {
                'type': 'bot',
                'text': f'Configuring switchport {mode} on {interface}',
                'commands': f'''enable
configure terminal
interface {interface}
switchport mode {mode}
no shutdown
exit''',
                'explanation': f'This configures {interface} as switchport mode {mode}'
            }
    
    # Static route
    if 'route' in input_lower and not 'rip' in input_lower:
        network_match = re.search(r'(?:network|to)\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_lower)
        gateway_match = re.search(r'(?:via|through|gateway)\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', input_lower)
        
        if network_match and gateway_match:
            network = network_match.group(1)
            gateway = gateway_match.group(1)
            mask = '255.255.255.0'
            
            return {
                'type': 'bot',
                'text': f'Adding static route to {network}',
                'commands': f'''enable
configure terminal
ip route {network} {mask} {gateway}
exit''',
                'explanation': f'This creates a static route to {network} via {gateway}'
            }
    
    # Security - passwords
    if 'password' in input_lower:
        password_match = re.search(r'(?:to|is|password)\s*([a-z0-9]+)', input_lower)
        if password_match:
            password = password_match.group(1)
            
            if 'enable secret' in input_lower:
                return {
                    'type': 'bot',
                    'text': 'Setting enable secret password',
                    'commands': f'''enable
configure terminal
enable secret {password}
exit''',
                    'explanation': 'This sets an encrypted enable password'
                }
            elif 'enable' in input_lower:
                return {
                    'type': 'bot',
                    'text': 'Setting enable password',
                    'commands': f'''enable
configure terminal
enable password {password}
exit''',
                    'explanation': 'This sets the enable password'
                }
            elif 'console' in input_lower:
                return {
                    'type': 'bot',
                    'text': 'Setting console password',
                    'commands': f'''enable
configure terminal
line console 0
password {password}
login
exit''',
                    'explanation': 'This sets the console line password'
                }
    
    # Show commands
    if 'show' in input_lower:
        if 'ip' in input_lower and 'brief' in input_lower:
            return {
                'type': 'bot',
                'text': 'Show IP interface brief',
                'commands': 'show ip interface brief',
                'explanation': 'Displays summary of all interfaces'
            }
        elif 'ip' in input_lower and 'route' in input_lower:
            return {
                'type': 'bot',
                'text': 'Show IP routing table',
                'commands': 'show ip route',
                'explanation': 'Displays the routing table'
            }
        elif 'running' in input_lower or 'config' in input_lower:
            return {
                'type': 'bot',
                'text': 'Show running configuration',
                'commands': 'show running-config',
                'explanation': 'Displays current configuration'
            }
        elif 'version' in input_lower:
            return {
                'type': 'bot',
                'text': 'Show version',
                'commands': 'show version',
                'explanation': 'Displays device information'
            }
        elif 'interface' in input_lower:
            return {
                'type': 'bot',
                'text': 'Show interfaces',
                'commands': 'show interfaces',
                'explanation': 'Displays all interface details'
            }
    
    # If no match found
    return {
        'type': 'bot',
        'text': '''I didn't understand that command. Here are some suggestions:

- Type "help" for all commands
- Type "help basic" for basic configuration
- Type "help ip" for IP configuration
- Type "show commands for R1" for device configuration

Or try asking naturally like:
"How do I set the hostname to R1?"
"Configure IP 192.168.1.1 on gigabitEthernet0/0"''',
        'commands': None,
        'explanation': None
    }

def normalize_typos(text):
    """Normalize common typos"""
    replacements = {
        'shwo': 'show',
        'confi': 'configure',
        'cofig': 'config',
        'interf': 'interface',
        'hosname': 'hostname',
        'runing': 'running',
        'runnig': 'running',
        'shutdwon': 'shutdown',
        'shutdonw': 'shutdown'
    }
    
    for typo, correct in replacements.items():
        text = text.replace(typo, correct)
    
    return text

def extract_help_category(text):
    """Extract help category from user input"""
    categories = ['basic', 'ip', 'routing', 'switch', 'security', 'show', 'rip', 'all']
    
    words = text.split()
    for category in categories:
        if category in words:
            return category
    
    return 'all'

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  CISCO IOS CONFIGURATION CHATBOT - SECURE WEB APP")
    print("="*60)
    print("\n  🌐 Open your browser and go to:")
    print("     http://127.0.0.1:5000")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)