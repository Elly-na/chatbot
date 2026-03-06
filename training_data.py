# Training data - teaching the chatbot different ways to say the same thing

TRAINING_PATTERNS = {
    'show_device': {
        'patterns': [
            'show device',
            'display device',
            'device info',
            'device information',
            'what is the device',
            'tell me about the device',
            'show me the device',
            'device details',
            'view device',
            'get device info',
            'device status',
            'show router',
            'display router info'
        ],
        'response_template': 'Device Information:\nHostname: {hostname}\nInterface: {interface}\nStatus: {status}'
    },
    
    'show_ip': {
        'patterns': [
            'show ip',
            'display ip',
            'what is the ip',
            'show ip address',
            'ip address',
            'what ip address',
            'tell me the ip',
            'get ip',
            'view ip',
            'show me the ip',
            'ip configuration',
            'display ip config',
            'what is my ip'
        ],
        'response_template': 'IP Configuration:\nIP Address: {ip_address}\nInterface: {interface}\nStatus: {status}'
    },
    
    'configure_ip': {
        'patterns': [
            'configure ip {ip}',
            'set ip {ip}',
            'set ip to {ip}',
            'change ip to {ip}',
            'assign ip {ip}',
            'ip address {ip}',
            'make ip {ip}',
            'configure ip address {ip}',
            'set the ip to {ip}',
            'change ip address to {ip}'
        ],
        'response_template': '✓ IP address configured to {ip}'
    },
    
    'set_hostname': {
        'patterns': [
            'set hostname {name}',
            'change hostname {name}',
            'hostname {name}',
            'rename to {name}',
            'call it {name}',
            'name it {name}',
            'set device name {name}',
            'change name to {name}',
            'set the hostname to {name}'
        ],
        'response_template': '✓ Hostname changed to {name}'
    },
    
    'enable_interface': {
        'patterns': [
            'enable interface',
            'turn on interface',
            'interface up',
            'start interface',
            'activate interface',
            'bring up interface',
            'turn interface on',
            'enable port',
            'switch on interface'
        ],
        'response_template': '✓ Interface {interface} is now UP'
    },
    
    'disable_interface': {
        'patterns': [
            'disable interface',
            'turn off interface',
            'interface down',
            'stop interface',
            'deactivate interface',
            'shut down interface',
            'turn interface off',
            'disable port'
        ],
        'response_template': '✓ Interface {interface} is now DOWN'
    },
    
    'show_config': {
        'patterns': [
            'show config',
            'show configuration',
            'display config',
            'view config',
            'full config',
            'running config',
            'show running config',
            'display configuration',
            'get config',
            'configuration details'
        ],
        'response_template': 'Current Configuration:\n{config}'
    },
    
    'greeting': {
        'patterns': [
            'hello',
            'hi',
            'hey',
            'good morning',
            'good afternoon',
            'good evening',
            'greetings',
            'hi there',
            'hello there'
        ],
        'response_template': 'Hello! I\'m your Network Configuration Assistant. Type "help" to see what I can do.'
    },
    
    'help': {
        'patterns': [
            'help',
            'help me',
            'what can you do',
            'commands',
            'show commands',
            'available commands',
            'how to use',
            'guide',
            'what commands'
        ],
        'response_template': '''Available commands:
- show device - Display device information
- show ip - Display IP configuration  
- configure ip [address] - Set IP address
- set hostname [name] - Change hostname
- enable interface - Turn on interface
- disable interface - Turn off interface
- show config - Display full configuration'''
    }
}