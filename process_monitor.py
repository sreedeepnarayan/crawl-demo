#!/usr/bin/env python3
"""
Process Monitor Web Interface
A simple Flask app to monitor and manage development processes
"""
import subprocess
import json
import re
import os
import psutil
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_processes():
    """Get all relevant development processes"""
    try:
        processes = []
        
        # Get all processes for current user
        current_user = subprocess.check_output(['whoami']).decode().strip()
        
        # Get all listening ports first
        port_map = get_port_mappings()
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time', 'status']):
            try:
                pinfo = proc.info
                
                # Skip if not our user's process
                if proc.username() != current_user:
                    continue
                
                cmdline = ' '.join(pinfo['cmdline']) if pinfo['cmdline'] else ''
                
                # Filter for development-related processes
                if any(keyword in cmdline.lower() for keyword in [
                    'python', 'node', 'npm', 'php', 'mysql', 'postgres', 'docker',
                    'mcp-server', 'flask', 'django', 'next', 'playwright', 'artisan'
                ]):
                    # Get working directory
                    try:
                        cwd = proc.cwd()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        cwd = None
                    
                    # Detect service and repository
                    service, repo = detect_service_repo(cmdline, pinfo['name'], cwd)
                    category = service  # For backward compatibility
                    
                    # Get memory usage in MB
                    memory_mb = pinfo['memory_info'].rss / 1024 / 1024 if pinfo['memory_info'] else 0
                    
                    # Get start time
                    start_time = datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Get ports for this process
                    ports = port_map.get(pinfo['pid'], [])
                    
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                        'full_cmdline': cmdline,
                        'cpu_percent': round(pinfo['cpu_percent'], 2),
                        'memory_mb': round(memory_mb, 2),
                        'start_time': start_time,
                        'status': pinfo['status'],
                        'category': category,
                        'service': service,
                        'repo': repo,
                        'priority': get_priority(category, cmdline),
                        'ports': ports
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        # Sort by priority (high impact first) then by memory usage
        processes.sort(key=lambda x: (x['priority'], -x['memory_mb']))
        
        return processes
        
    except Exception as e:
        return [{'error': str(e)}]

def get_port_mappings():
    """Get mapping of PIDs to their listening ports"""
    port_map = {}
    
    try:
        # Try psutil first (faster when it works)
        connections = psutil.net_connections(kind='inet')
        
        for conn in connections:
            if conn.status == 'LISTEN' and conn.pid:
                if conn.pid not in port_map:
                    port_map[conn.pid] = []
                
                port_info = {
                    'port': conn.laddr.port,
                    'address': conn.laddr.ip,
                    'type': 'TCP'
                }
                
                # Add common port names
                port_info['name'] = get_port_name(conn.laddr.port)
                
                port_map[conn.pid].append(port_info)
                
    except (psutil.AccessDenied, psutil.NoSuchProcess, PermissionError):
        # Fallback to lsof command (more reliable on macOS)
        try:
            result = subprocess.run(
                ['lsof', '-i', '-P', '-n', '-sTCP:LISTEN'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 9:
                        pid = int(parts[1])
                        name_addr = parts[8]  # Format: *:port or ip:port
                        
                        if ':' in name_addr:
                            addr_part, port_part = name_addr.rsplit(':', 1)
                            try:
                                port = int(port_part)
                                address = addr_part if addr_part != '*' else '0.0.0.0'
                                
                                if pid not in port_map:
                                    port_map[pid] = []
                                
                                port_info = {
                                    'port': port,
                                    'address': address,
                                    'type': 'TCP',
                                    'name': get_port_name(port)
                                }
                                
                                port_map[pid].append(port_info)
                                
                            except ValueError:
                                continue
                                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            # lsof not available or failed
            pass
    
    return port_map

def get_port_name(port):
    """Get common name for well-known development ports"""
    port_names = {
        3000: 'React/Next.js',
        3001: 'React Dev',
        4000: 'Phoenix/Rails',
        5000: 'Flask/Registry',
        5001: 'Flask Dev',
        5003: 'Custom App',
        5432: 'PostgreSQL',
        5555: 'Crawl4AI Demo',
        5556: 'Process Monitor',
        6379: 'Redis',
        8000: 'Django/Laravel',
        8080: 'Web Server',
        8081: 'Alt Web Server',
        8888: 'Jupyter',
        9000: 'PHP-FPM',
        27017: 'MongoDB',
        3306: 'MySQL'
    }
    return port_names.get(port, '')

def detect_service_repo(cmdline, name, cwd=None):
    """Detect service/repo from command line and working directory"""
    cmdline_lower = cmdline.lower()
    
    # Service detection
    service = 'Other'
    repo = 'Unknown'
    
    # Detect service type
    if 'mcp-server-playwright' in cmdline_lower:
        service = 'Playwright MCP'
    elif 'next dev' in cmdline_lower or 'turbopack' in cmdline_lower:
        service = 'Next.js Dev'
    elif 'artisan serve' in cmdline_lower or ('php' in cmdline_lower and 'serve' in cmdline_lower):
        service = 'Laravel Dev'
    elif 'simple_web_demo' in cmdline_lower or 'process_monitor' in cmdline_lower:
        service = 'Current Demo'
    elif 'playwright test' in cmdline_lower:
        service = 'Playwright Tests'
    elif 'docker' in cmdline_lower or name.lower() == 'com.docker.backend':
        service = 'Docker'
    elif 'mysql' in cmdline_lower or 'mysqld' in cmdline_lower:
        service = 'MySQL'
    elif 'postgres' in cmdline_lower:
        service = 'PostgreSQL'
    elif 'code helper' in cmdline_lower or 'code' in name.lower():
        service = 'VS Code'
    elif 'npm' in cmdline_lower:
        service = 'NPM'
    elif 'node' in cmdline_lower and 'server' in cmdline_lower:
        service = 'Node.js Server'
    elif 'python' in cmdline_lower and ('flask' in cmdline_lower or 'django' in cmdline_lower):
        service = 'Python Web'
    elif 'python' in cmdline_lower:
        service = 'Python'
    elif 'chrome' in name.lower():
        service = 'Chrome'
    
    # Detect repository from working directory or command path
    if cwd:
        cwd_lower = cwd.lower()
        if 'atari-agreements' in cwd_lower:
            repo = 'atari-agreements'
        elif 'atarifusionrepo' in cwd_lower:
            repo = 'AtariFusionRepo'
        elif 'portfolio-3d' in cwd_lower:
            repo = 'portfolio-3d'
        elif 'crawl' in cwd_lower and 'workspace' in cwd_lower:
            repo = 'crawl-poc'
        elif 'n8n' in cwd_lower:
            repo = 'n8n'
        elif 'ai-engineering' in cwd_lower:
            repo = 'ai-engineering'
        elif 'pdf-ocr-tool' in cwd_lower:
            repo = 'pdf-ocr-tool'
    
    # Fallback: detect repo from command line path
    if repo == 'Unknown' and '/' in cmdline:
        if 'atari-agreements' in cmdline_lower:
            repo = 'atari-agreements'
        elif 'atarifusionrepo' in cmdline_lower:
            repo = 'AtariFusionRepo'
        elif 'portfolio-3d' in cmdline_lower:
            repo = 'portfolio-3d'
        elif 'crawl' in cmdline_lower:
            repo = 'crawl-poc'
        elif 'n8n' in cmdline_lower:
            repo = 'n8n'
    
    # Special cases for system services
    if service in ['PostgreSQL', 'MySQL', 'Docker'] and repo == 'Unknown':
        repo = 'System'
    elif service in ['Chrome', 'VS Code'] and repo == 'Unknown':
        repo = 'Applications'
    
    return service, repo

def categorize_process(cmdline, name):
    """Categorize process based on command line (legacy function)"""
    service, _ = detect_service_repo(cmdline, name)
    return service

def get_priority(category, cmdline):
    """Get priority for sorting (lower number = higher priority to kill)"""
    high_impact = ['Playwright MCP', 'Next.js Dev', 'Playwright Tests']
    medium_impact = ['Laravel Dev', 'Node/NPM']
    keep_running = ['Current Demo', 'MySQL', 'PostgreSQL', 'VS Code']
    
    if category in high_impact:
        return 1
    elif category in medium_impact:
        return 2
    elif category in keep_running:
        return 4
    else:
        return 3

@app.route('/')
def index():
    """Main monitoring page"""
    return render_template('process_monitor.html')

@app.route('/api/processes')
def get_processes_api():
    """Get all processes as JSON"""
    processes = get_processes()
    
    # Add summary statistics
    summary = {
        'total_processes': len(processes),
        'high_priority_count': len([p for p in processes if p.get('priority') == 1]),
        'total_memory_mb': sum(p.get('memory_mb', 0) for p in processes),
        'total_cpu_percent': sum(p.get('cpu_percent', 0) for p in processes)
    }
    
    return jsonify({
        'processes': processes,
        'summary': summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/kill/<int:pid>', methods=['POST'])
def kill_process(pid):
    """Kill a process by PID"""
    try:
        # Get process info first
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc_cmdline = ' '.join(proc.cmdline())
        
        # Kill the process
        proc.kill()
        
        return jsonify({
            'success': True,
            'message': f'Successfully killed process {pid} ({proc_name})',
            'pid': pid,
            'name': proc_name
        })
        
    except psutil.NoSuchProcess:
        return jsonify({
            'success': False,
            'error': f'Process {pid} not found (already terminated?)'
        }), 404
        
    except psutil.AccessDenied:
        return jsonify({
            'success': False,
            'error': f'Permission denied to kill process {pid}'
        }), 403
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/kill-category', methods=['POST'])
def kill_category():
    """Kill all processes in a category"""
    try:
        data = request.get_json()
        category = data.get('category')
        
        if not category:
            return jsonify({'success': False, 'error': 'Category is required'}), 400
        
        processes = get_processes()
        killed_count = 0
        errors = []
        
        for proc_info in processes:
            if proc_info.get('category') == category:
                try:
                    proc = psutil.Process(proc_info['pid'])
                    proc.kill()
                    killed_count += 1
                except Exception as e:
                    errors.append(f"PID {proc_info['pid']}: {str(e)}")
        
        return jsonify({
            'success': True,
            'killed_count': killed_count,
            'errors': errors,
            'message': f'Killed {killed_count} processes in category "{category}"'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/restart/<int:pid>', methods=['POST'])
def restart_process(pid):
    """Restart a process by killing it and starting a new one with the same command"""
    try:
        # Get process info first
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc_cmdline = proc.cmdline()
        proc_cwd = proc.cwd()
        
        if not proc_cmdline:
            return jsonify({
                'success': False,
                'error': f'Cannot restart process {pid}: No command line available'
            }), 400
        
        # Kill the process
        proc.kill()
        
        # Wait a moment for the process to fully terminate
        import time
        time.sleep(1)
        
        # Try to restart with the same command
        try:
            # Use subprocess to start the new process
            new_proc = subprocess.Popen(
                proc_cmdline,
                cwd=proc_cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            return jsonify({
                'success': True,
                'message': f'Successfully restarted process {proc_name}',
                'old_pid': pid,
                'new_pid': new_proc.pid,
                'command': ' '.join(proc_cmdline)
            })
            
        except Exception as restart_error:
            return jsonify({
                'success': False,
                'error': f'Killed process {pid} but failed to restart: {str(restart_error)}',
                'killed': True
            }), 500
        
    except psutil.NoSuchProcess:
        return jsonify({
            'success': False,
            'error': f'Process {pid} not found (already terminated?)'
        }), 404
        
    except psutil.AccessDenied:
        return jsonify({
            'success': False,
            'error': f'Permission denied to restart process {pid}'
        }), 403
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ports')
def get_ports():
    """Get all listening ports with process information, aggregated by port number"""
    try:
        port_map = get_port_mappings()
        aggregated_ports = {}
        
        for pid, ports in port_map.items():
            try:
                proc = psutil.Process(pid)
                proc_name = proc.name()
                proc_cmdline = ' '.join(proc.cmdline())
                
                # Get working directory for service/repo detection
                try:
                    cwd = proc.cwd()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    cwd = None
                
                # Detect service and repository
                service, repo = detect_service_repo(proc_cmdline, proc_name, cwd)
                
                for port_info in ports:
                    port_num = port_info['port']
                    
                    if port_num not in aggregated_ports:
                        aggregated_ports[port_num] = {
                            'port': port_num,
                            'name': port_info['name'],
                            'type': port_info['type'],
                            'processes': [],
                            'services': set(),
                            'repos': set()
                        }
                    
                    # Add process info to this port
                    process_info = {
                        'pid': pid,
                        'process_name': proc_name,
                        'command': proc_cmdline[:100] + '...' if len(proc_cmdline) > 100 else proc_cmdline,
                        'address': port_info['address'],
                        'service': service,
                        'repo': repo
                    }
                    
                    # Avoid duplicates (same PID might have multiple addresses for same port)
                    if not any(p['pid'] == pid for p in aggregated_ports[port_num]['processes']):
                        aggregated_ports[port_num]['processes'].append(process_info)
                        aggregated_ports[port_num]['services'].add(service)
                        aggregated_ports[port_num]['repos'].add(repo)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Convert to list and convert sets to lists for JSON serialization
        port_list = []
        all_services = set()
        all_repos = set()
        
        for port_data in aggregated_ports.values():
            port_data['services'] = list(port_data['services'])
            port_data['repos'] = list(port_data['repos'])
            port_list.append(port_data)
            all_services.update(port_data['services'])
            all_repos.update(port_data['repos'])
        
        # Sort by port number
        port_list.sort(key=lambda x: x['port'])
        
        return jsonify({
            'ports': port_list,
            'total_ports': len(port_list),
            'total_processes': sum(len(port['processes']) for port in port_list),
            'available_services': sorted(list(all_services)),
            'available_repos': sorted(list(all_repos))
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-service', methods=['POST'])
def start_service():
    """Start a service based on repository and service type"""
    try:
        data = request.get_json()
        repo = data.get('repo')
        service = data.get('service')
        
        if not repo or not service:
            return jsonify({'success': False, 'error': 'Repository and service are required'}), 400
        
        # Define start commands for different services in different repos
        start_commands = {
            'atari-agreements': {
                'Laravel Dev': 'cd ../atari-agreements/backend && php artisan serve --host=0.0.0.0 --port=8001',
                'Next.js Dev': 'cd ../atari-agreements/frontend && npm run dev'
            },
            'portfolio-3d': {
                'Next.js Dev': 'cd ../portfolio-3d && npm run dev'
            },
            'crawl-poc': {
                'Current Demo': 'cd . && python simple_web_demo.py',
                'Process Monitor': 'cd . && python process_monitor.py'
            },
            'pdf-ocr-tool': {
                'Python Web': 'cd ../pdf-ocr-tool && bash start-web.sh > pdf_ocr_output.log 2>&1',
                'Flask App': 'cd ../pdf-ocr-tool && python main.py > pdf_ocr_output.log 2>&1',
                'Main Script': 'cd ../pdf-ocr-tool && python main.py > pdf_ocr_output.log 2>&1'
            }
        }
        
        # Check if we have a predefined start command
        if repo in start_commands and service in start_commands[repo]:
            command = start_commands[repo][service]
        else:
            # For other services, try to provide a generic response or suggest alternative
            return jsonify({
                'success': False, 
                'error': f'Cannot automatically start {service} in {repo}. Please start manually or add start command configuration.',
                'suggestion': f'This service ({service}) needs to be started manually from its respective application or terminal.'
            }), 400
        
        # Start the service in background
        try:
            proc = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            return jsonify({
                'success': True,
                'message': f'Started {service} for {repo}',
                'pid': proc.pid,
                'command': command
            })
            
        except Exception as start_error:
            return jsonify({
                'success': False,
                'error': f'Failed to start service: {str(start_error)}'
            }), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stop-service', methods=['POST'])
def stop_service():
    """Stop all processes for a specific service in a repository"""
    try:
        data = request.get_json()
        repo = data.get('repo')
        service = data.get('service')
        
        if not repo or not service:
            return jsonify({'success': False, 'error': 'Repository and service are required'}), 400
        
        processes = get_processes()
        killed_count = 0
        killed_pids = []
        errors = []
        
        for proc_info in processes:
            if proc_info.get('repo') == repo and proc_info.get('service') == service:
                try:
                    proc = psutil.Process(proc_info['pid'])
                    proc.kill()
                    killed_count += 1
                    killed_pids.append(proc_info['pid'])
                except Exception as e:
                    errors.append(f"PID {proc_info['pid']}: {str(e)}")
        
        if killed_count == 0:
            return jsonify({
                'success': False,
                'error': f'No running processes found for {service} in {repo}'
            }), 404
        
        return jsonify({
            'success': True,
            'killed_count': killed_count,
            'killed_pids': killed_pids,
            'errors': errors,
            'message': f'Stopped {killed_count} processes for {service} in {repo}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug-start/<repo>/<service>')
def debug_start(repo, service):
    """Debug endpoint to test start commands"""
    start_commands = {
        'atari-agreements': {
            'Laravel Dev': 'cd ../atari-agreements/backend && php artisan serve --host=0.0.0.0 --port=8001',
            'Next.js Dev': 'cd ../atari-agreements/frontend && npm run dev'
        },
        'portfolio-3d': {
            'Next.js Dev': 'cd ../portfolio-3d && npm run dev'
        },
        'crawl-poc': {
            'Current Demo': 'cd . && python simple_web_demo.py',
            'Process Monitor': 'cd . && python process_monitor.py'
        },
        'pdf-ocr-tool': {
            'Python Web': 'cd ../pdf-ocr-tool && bash start-web.sh > pdf_ocr_output.log 2>&1',
            'Flask App': 'cd ../pdf-ocr-tool && python main.py > pdf_ocr_output.log 2>&1',
            'Main Script': 'cd ../pdf-ocr-tool && python main.py > pdf_ocr_output.log 2>&1'
        }
    }
    
    if repo in start_commands and service in start_commands[repo]:
        command = start_commands[repo][service]
        
        # Test if directory exists
        try:
            if repo == 'pdf-ocr-tool':
                test_result = subprocess.run(['ls', '../pdf-ocr-tool'], capture_output=True, text=True, timeout=5)
                return jsonify({
                    'command': command,
                    'directory_exists': test_result.returncode == 0,
                    'directory_contents': test_result.stdout.strip().split('\n') if test_result.returncode == 0 else None,
                    'error': test_result.stderr if test_result.stderr else None
                })
            else:
                return jsonify({'command': command, 'note': 'Directory test only available for pdf-ocr-tool'})
        except Exception as e:
            return jsonify({'error': f'Debug test failed: {str(e)}'})
    else:
        return jsonify({'error': f'No command found for {service} in {repo}'})

@app.route('/api/logs/services')
def get_log_services():
    """Get list of services that have log files available"""
    try:
        log_services = []
        
        # Add known log files for different services
        log_files = {
            'process-monitor': {
                'name': 'Process Monitor',
                'repo': 'crawl-poc',
                'files': ['process_monitor_*.log']
            },
            'crawl-demo': {
                'name': 'Crawl4AI Demo',
                'repo': 'crawl-poc', 
                'files': ['web_demo_working.log']
            },
            'pdf-ocr-tool': {
                'name': 'PDF OCR Tool',
                'repo': 'pdf-ocr-tool',
                'files': ['../pdf-ocr-tool/pdf_ocr_output.log', '../pdf-ocr-tool/server.log']
            }
        }
        
        # Check which log files actually exist
        for service_id, service_info in log_files.items():
            available_files = []
            for file_pattern in service_info['files']:
                if '*' in file_pattern:
                    # Handle glob patterns
                    import glob
                    files = glob.glob(file_pattern)
                    available_files.extend(files)
                else:
                    # Check single file
                    if os.path.exists(file_pattern):
                        available_files.append(file_pattern)
            
            if available_files:
                log_services.append({
                    'id': service_id,
                    'name': service_info['name'],
                    'repo': service_info['repo'],
                    'files': available_files
                })
        
        return jsonify({
            'success': True,
            'services': log_services
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/logs/<service_id>')
def get_service_logs(service_id):
    """Get logs for a specific service"""
    try:
        # Map service IDs to their log files
        log_files_map = {
            'process-monitor': ['process_monitor_*.log'],
            'crawl-demo': ['web_demo_working.log'],
            'pdf-ocr-tool': ['../pdf-ocr-tool/pdf_ocr_output.log', '../pdf-ocr-tool/server.log']
        }
        
        if service_id not in log_files_map:
            return jsonify({'success': False, 'error': 'Service not found'}), 404
        
        all_logs = []
        
        for file_pattern in log_files_map[service_id]:
            if '*' in file_pattern:
                # Handle glob patterns - get the most recent file
                import glob
                files = glob.glob(file_pattern)
                if files:
                    # Sort by modification time, get most recent
                    latest_file = max(files, key=os.path.getmtime)
                    file_pattern = latest_file
            
            if os.path.exists(file_pattern):
                try:
                    with open(file_pattern, 'r') as f:
                        # Get last 100 lines
                        lines = f.readlines()
                        recent_lines = lines[-100:] if len(lines) > 100 else lines
                        all_logs.extend([line.strip() for line in recent_lines])
                except Exception as e:
                    all_logs.append(f"Error reading {file_pattern}: {str(e)}")
        
        if not all_logs:
            all_logs = ["No logs found or logs are empty"]
        
        return jsonify({
            'success': True,
            'logs': all_logs,
            'service_id': service_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🖥️  Starting Process Monitor")
    print("=" * 40)
    print("🌐 Monitor available at: http://localhost:5556")
    print("📋 Features:")
    print("   - View all development processes")
    print("   - Kill individual processes") 
    print("   - Kill entire categories")
    print("   - Real-time resource monitoring")
    print("🔧 Press Ctrl+C to stop")
    print()
    
    app.run(debug=False, host='0.0.0.0', port=5556, threaded=True)