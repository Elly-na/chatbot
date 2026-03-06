import re

class CiscoCommandGenerator:
    def __init__(self):
        self.device_configs = {
            'R1': {
                'hostname': 'R1',
                'interfaces': {
                    'gigabitEthernet0/0': {
                        'ip': '192.168.10.1',
                        'mask': '255.255.255.0',
                        'status': 'no shutdown'
                    },
                    'serial0/3/0': {
                        'ip': '10.10.10.1',
                        'mask': '255.255.255.252',
                        'status': 'no shutdown'
                    }
                },
                'routes': ['ip route 192.168.20.0 255.255.255.0 10.10.10.2'],
                'rip': {
                    'version': 2,
                    'networks': ['192.168.10.0', '10.10.10.0']
                }
            },
            'R2': {
                'hostname': 'R2',
                'interfaces': {
                    'serial0/2/0': {
                        'ip': '10.10.10.2',
                        'mask': '255.255.255.252',
                        'status': 'no shutdown'
                    },
                    'gigabitEthernet0/0': {
                        'ip': '192.168.20.1',
                        'mask': '255.255.255.0',
                        'status': 'no shutdown'
                    }
                },
                'routes': ['ip route 192.168.10.0 255.255.255.0 10.10.10.1'],
                'rip': {
                    'version': 2,
                    'networks': ['192.168.20.0', '10.10.10.0']
                }
            },
            'S1': {
                'hostname': 'S1',
                'interfaces': {
                    'fastEthernet0/1': {
                        'mode': 'access',
                        'status': 'no shutdown'
                    },
                    'fastEthernet1/1': {
                        'mode': 'access',
                        'status': 'no shutdown'
                    }
                }
            },
            'S2': {
                'hostname': 'S2',
                'interfaces': {
                    'fastEthernet0/1': {
                        'mode': 'access',
                        'status': 'no shutdown'
                    },
                    'fastEthernet1/1': {
                        'mode': 'access',
                        'status': 'no shutdown'
                    }
                }
            }
        }
    
    def generate_commands(self, user_input):
        """Generate Cisco commands based on user input"""
        input_lower = user_input.lower().strip()
        
        # Help command
        if input_lower == 'help' or 'help me' in input_lower:
            return {
                'description': 'Available Commands',
                'commands': '''HOSTNAME CONFIGURATION:
- "set hostname to R2"

IP ADDRESS CONFIGURATION:
- "configure ip 192.168.10.1 on interface gigabitEthernet0/0"
- "configure ip 10.0.0.1 mask 255.255.255.0 on serial0/3/0"

INTERFACE MANAGEMENT:
- "enable interface fastEthernet0/1"
- "disable interface gigabitEthernet0/0"

SWITCHPORT CONFIGURATION:
- "configure switchport mode access on fastEthernet0/1"
- "configure switchport mode trunk on fastEthernet1/1"

STATIC ROUTING:
- "add route to network 192.168.20.0 via 10.10.10.2"

RIP ROUTING:
- "configure RIP on R1"
- "configure RIP routing on R2"

DEVICE CONFIGURATIONS:
- "show commands for R1"
- "show commands for R2"
- "show commands for S1"

SHOW COMMANDS:
- "show ip interface brief"
- "show ip route"
- "show running-config"''',
                'explanation': 'These are all available commands. Try any of them!'
            }
        
        # Set hostname
        if 'hostname' in input_lower:
            match = re.search(r'(?:hostname|to)\s+([a-z0-9]+)', input_lower)
            if match:
                hostname = match.group(1).upper()
                return {
                    'description': f'Setting hostname to {hostname}',
                    'commands': f'''enable
configure terminal
hostname {hostname}
exit''',
                    'explanation': f'This sets the device hostname to "{hostname}"'
                }
        
        # Configure IP address
        if 'ip' in input_lower and ('interface' in input_lower or 'int' in input_lower):
            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', input_lower)
            int_match = re.search(r'(?:interface|int|on)\s+([a-z0-9\/]+)', input_lower)
            mask_match = re.search(r'mask\s+(\d+\.\d+\.\d+\.\d+)', input_lower)
            
            if ip_match and int_match:
                ip = ip_match.group(0)
                intf = int_match.group(1)
                mask = mask_match.group(1) if mask_match else '255.255.255.0'
                
                return {
                    'description': f'Configuring IP {ip} on {intf}',
                    'commands': f'''enable
configure terminal
interface {intf}
ip address {ip} {mask}
no shutdown
exit''',
                    'explanation': f'This assigns IP address {ip} with subnet mask {mask} to interface {intf} and enables it'
                }
        
        # Enable interface
        if ('enable' in input_lower or 'turn on' in input_lower or 'no shut' in input_lower) and 'interface' in input_lower:
            int_match = re.search(r'(?:interface|int)\s+([a-z0-9\/]+)', input_lower)
            if int_match:
                intf = int_match.group(1)
                return {
                    'description': f'Enabling interface {intf}',
                    'commands': f'''enable
configure terminal
interface {intf}
no shutdown
exit''',
                    'explanation': f'This enables (brings up) interface {intf}'
                }
        
        # Disable interface
        if ('disable' in input_lower or 'shut down' in input_lower or 'shutdown' in input_lower) and 'interface' in input_lower:
            int_match = re.search(r'(?:interface|int)\s+([a-z0-9\/]+)', input_lower)
            if int_match:
                intf = int_match.group(1)
                return {
                    'description': f'Disabling interface {intf}',
                    'commands': f'''enable
configure terminal
interface {intf}
shutdown
exit''',
                    'explanation': f'This disables (shuts down) interface {intf}'
                }
        
        # Configure switchport
        if 'switchport' in input_lower:
            int_match = re.search(r'(?:interface|int|on)\s+([a-z0-9\/]+)', input_lower)
            mode_match = re.search(r'mode\s+(access|trunk)', input_lower)
            
            if int_match:
                intf = int_match.group(1)
                mode = mode_match.group(1) if mode_match else 'access'
                
                return {
                    'description': f'Configuring switchport {mode} on {intf}',
                    'commands': f'''enable
configure terminal
interface {intf}
switchport mode {mode}
no shutdown
exit''',
                    'explanation': f'This configures interface {intf} as a switchport in {mode} mode'
                }
        
        # Static route
        if 'route' in input_lower and not 'rip' in input_lower:
            network_match = re.search(r'network\s+(\d+\.\d+\.\d+\.\d+)', input_lower)
            mask_match = re.search(r'mask\s+(\d+\.\d+\.\d+\.\d+)', input_lower)
            next_hop_match = re.search(r'(?:next hop|gateway|via)\s+(\d+\.\d+\.\d+\.\d+)', input_lower)
            
            if network_match and next_hop_match:
                network = network_match.group(1)
                mask = mask_match.group(1) if mask_match else '255.255.255.0'
                next_hop = next_hop_match.group(1)
                
                return {
                    'description': f'Adding static route to {network}',
                    'commands': f'''enable
configure terminal
ip route {network} {mask} {next_hop}
exit''',
                    'explanation': f'This creates a static route to network {network}/{mask} via next hop {next_hop}'
                }
        
        # Show commands for specific device
        if 'show' in input_lower and ('commands' in input_lower or 'configuration' in input_lower):
            device_match = re.search(r'(?:for|device)\s+(r[12]|s[12])', input_lower)
            if device_match:
                device = device_match.group(1).upper()
                config = self.device_configs.get(device)
                
                if config:
                    commands = f'''enable
configure terminal
hostname {config['hostname']}\n'''
                    
                    for intf, conf in config['interfaces'].items():
                        commands += f'''interface {intf}\n'''
                        if 'ip' in conf:
                            commands += f'''ip address {conf['ip']} {conf['mask']}\n'''
                        if 'mode' in conf:
                            commands += f'''switchport mode {conf['mode']}\n'''
                        commands += f'''{conf['status']}\n'''
                    
                    if 'routes' in config:
                        for route in config['routes']:
                            commands += f'''{route}\n'''
                    
                    commands += 'exit'
                    
                    return {
                        'description': f'Complete configuration for {device}',
                        'commands': commands,
                        'explanation': f'This is the complete Cisco IOS configuration for device {device}'
                    }
        
        # Show IP interface brief
        if 'show ip' in input_lower or 'sh ip' in input_lower:
            return {
                'description': 'Show IP interface status',
                'commands': 'show ip interface brief',
                'explanation': 'This displays a summary of all interfaces with their IP addresses and status'
            }
        
        # Show IP route
        if 'show' in input_lower and 'route' in input_lower and 'ip' in input_lower:
            return {
                'description': 'Show routing table',
                'commands': 'show ip route',
                'explanation': 'This displays the routing table with all configured routes'
            }
        
        # Show running config
        if 'show' in input_lower and ('running' in input_lower or 'config' in input_lower):
            return {
                'description': 'Show running configuration',
                'commands': 'show running-config',
                'explanation': 'This displays the current running configuration'
            }
        
        # Configure RIP routing
        if 'rip' in input_lower:
            device_match = re.search(r'(?:for|on|device)\s+(r[12])', input_lower)
            if device_match:
                device = device_match.group(1).upper()
                config = self.device_configs.get(device)
                
                if config and 'rip' in config:
                    rip = config['rip']
                    commands = f'''enable
configure terminal
router rip
version {rip['version']}
no auto-summary\n'''
                    
                    for network in rip['networks']:
                        commands += f'''network {network}\n'''
                    
                    commands += '''end
write memory'''
                    
                    return {
                        'description': f'Configuring RIP routing on {device}',
                        'commands': commands,
                        'explanation': f'This configures RIPv{rip["version"]} routing protocol on {device} with networks: {", ".join(rip["networks"])}'
                    }
            
            # Generic RIP
            return {
                'description': 'Configure RIP routing protocol',
                'commands': '''enable
configure terminal
router rip
version 2
no auto-summary
network [NETWORK_ADDRESS]
end
write memory''',
                'explanation': 'This is a template for configuring RIPv2. Replace [NETWORK_ADDRESS] with your network addresses.'
            }
        
        return None