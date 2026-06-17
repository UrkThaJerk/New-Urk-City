"""
Real-time Web Dashboard for Gamified Agent Ecosystem
Provides live visualization of agent activity, leaderboards, and achievements
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
from agent_ecosystem import GameifiedAgentEcosystem, TaskType
import threading
import time


app = Flask(__name__)
CORS(app)

# Global ecosystem instance
ecosystem = GameifiedAgentEcosystem()


# ===================== HTML DASHBOARD TEMPLATE =====================
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Gamified Agent Ecosystem Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #00d4ff;
            padding-bottom: 20px;
        }
        
        header h1 {
            font-size: 2.5em;
            text-shadow: 0 0 20px #00d4ff;
            margin-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
        }
        
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #00d4ff;
            margin: 10px 0;
        }
        
        .stat-card .label {
            font-size: 0.9em;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .panel {
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border: 2px solid #00d4ff;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.2);
        }
        
        .panel h2 {
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #00d4ff;
            padding-bottom: 10px;
        }
        
        .leaderboard {
            list-style: none;
        }
        
        .leaderboard-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: rgba(0, 212, 255, 0.05);
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 3px solid #00d4ff;
            transition: all 0.3s ease;
        }
        
        .leaderboard-item:hover {
            background: rgba(0, 212, 255, 0.15);
            transform: translateX(5px);
        }
        
        .rank {
            font-weight: bold;
            color: #00d4ff;
            font-size: 1.2em;
            width: 30px;
        }
        
        .rank.top-1 { color: #ffd700; }
        .rank.top-2 { color: #c0c0c0; }
        .rank.top-3 { color: #cd7f32; }
        
        .agent-info {
            flex: 1;
            margin: 0 15px;
        }
        
        .agent-name {
            font-weight: bold;
            color: #fff;
        }
        
        .agent-role {
            font-size: 0.85em;
            color: #aaa;
        }
        
        .agent-stats {
            display: flex;
            gap: 10px;
            font-size: 0.9em;
        }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        
        .agent-card {
            background: rgba(0, 212, 255, 0.05);
            border: 2px solid #00d4ff;
            border-radius: 8px;
            padding: 15px;
            transition: all 0.3s ease;
        }
        
        .agent-card:hover {
            background: rgba(0, 212, 255, 0.15);
            transform: scale(1.05);
        }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .agent-name-badge {
            font-weight: bold;
            color: #00d4ff;
        }
        
        .status-badge {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .status-working {
            background: #ff6b6b;
            color: #fff;
        }
        
        .status-idle {
            background: #51cf66;
            color: #fff;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(0, 212, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin: 8px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #0099ff);
            transition: width 0.3s ease;
        }
        
        .level-badge {
            display: inline-block;
            background: #ffd700;
            color: #000;
            padding: 3px 8px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .event-log {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .event-item {
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(0, 212, 255, 0.05);
            border-left: 3px solid #00d4ff;
            border-radius: 3px;
            font-size: 0.9em;
        }
        
        .event-timestamp {
            color: #00d4ff;
            font-weight: bold;
        }
        
        .event-type {
            color: #aaa;
            font-style: italic;
        }
        
        .achievements {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }
        
        .achievement {
            font-size: 1.5em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .achievement:hover {
            transform: scale(1.2);
        }
        
        button {
            background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
        }
        
        .refresh-timer {
            text-align: center;
            margin-top: 20px;
            color: #aaa;
            font-size: 0.9em;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 212, 255, 0.1);
        }
        
        ::-webkit-scrollbar-thumb {
            background: #00d4ff;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 GAMIFIED AGENT ECOSYSTEM</h1>
            <p id="subtitle">Real-time Agent Management & Performance Tracking</p>
        </header>
        
        <!-- ECOSYSTEM STATS -->
        <div class="stats-grid" id="statsGrid">
            <div class="stat-card">
                <div class="label">Active Agents</div>
                <div class="value" id="activeAgents">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Total XP</div>
                <div class="value" id="totalXP">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Tasks Completed</div>
                <div class="value" id="tasksCompleted">0</div>
            </div>
            <div class="stat-card">
                <div class="label">Success Rate</div>
                <div class="value" id="successRate">0%</div>
            </div>
        </div>
        
        <!-- MAIN CONTENT -->
        <div class="main-grid">
            <!-- LEFT: ALL AGENTS -->
            <div>
                <div class="panel">
                    <h2>👥 All Agents</h2>
                    <div class="agents-grid" id="agentsGrid">
                        <p style="color: #aaa;">Loading agents...</p>
                    </div>
                    <button onclick="addRandomAgent()">+ Add Agent</button>
                    <button onclick="assignRandomTask()">⚡ Assign Random Task</button>
                </div>
                
                <!-- EVENT LOG -->
                <div class="panel" style="margin-top: 20px;">
                    <h2>📝 Recent Events</h2>
                    <div class="event-log" id="eventLog">
                        <p style="color: #aaa;">No events yet...</p>
                    </div>
                </div>
            </div>
            
            <!-- RIGHT: LEADERBOARD -->
            <div>
                <div class="panel">
                    <h2>🏆 Leaderboard</h2>
                    <ul class="leaderboard" id="leaderboard">
                        <li style="color: #aaa; text-align: center; padding: 20px;">Loading...</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="refresh-timer">
            <p>Auto-refreshing every 2 seconds...</p>
        </div>
    </div>
    
    <script>
        // Fetch and update dashboard data
        async function updateDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();
                
                // Update stats
                document.getElementById('activeAgents').textContent = data.ecosystem_stats.active_agents;
                document.getElementById('totalXP').textContent = data.ecosystem_stats.total_xp;
                document.getElementById('tasksCompleted').textContent = data.ecosystem_stats.completed_tasks;
                document.getElementById('successRate').textContent = data.ecosystem_stats.success_rate + '%';
                
                // Update agents grid
                updateAgentsGrid(data.agents);
                
                // Update leaderboard
                updateLeaderboard(data.leaderboard);
                
                // Update event log
                updateEventLog(data.recent_events);
                
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }
        
        function updateAgentsGrid(agents) {
            const grid = document.getElementById('agentsGrid');
            
            if (Object.keys(agents).length === 0) {
                grid.innerHTML = '<p style="color: #aaa;">No agents yet. Create one to get started!</p>';
                return;
            }
            
            grid.innerHTML = Object.values(agents).map(agent => `
                <div class="agent-card">
                    <div class="agent-header">
                        <div class="agent-name-badge">${agent.name}</div>
                        <span class="status-badge ${agent.status === 'working' ? 'status-working' : 'status-idle'}">
                            ${agent.status.toUpperCase()}
                        </span>
                    </div>
                    <div style="font-size: 0.85em; color: #aaa;">${agent.role}</div>
                    
                    <div style="margin: 10px 0; font-size: 0.9em;">
                        <div>📊 Level: <strong>${agent.stats.level}</strong></div>
                        <div>⚡ XP: <strong>${agent.stats.total_xp}</strong></div>
                        <div>✅ Tasks: <strong>${agent.stats.tasks_completed}</strong></div>
                        <div>🎯 Accuracy: <strong>${agent.stats.accuracy_score.toFixed(1)}%</strong></div>
                    </div>
                    
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${(agent.stats.accuracy_score)}%"></div>
                    </div>
                    
                    ${agent.stats.level > 1 ? `<div class="level-badge">LV ${agent.stats.level}</div>` : ''}
                    
                    ${Object.keys(agent.achievements).length > 0 ? `
                        <div class="achievements">
                            ${Object.values(agent.achievements).map(ach => 
                                `<div class="achievement" title="${ach.name}">${ach.icon}</div>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }
        
        function updateLeaderboard(leaderboard) {
            const list = document.getElementById('leaderboard');
            
            if (leaderboard.length === 0) {
                list.innerHTML = '<li style="color: #aaa; text-align: center; padding: 20px;">No agents yet</li>';
                return;
            }
            
            list.innerHTML = leaderboard.map((agent, idx) => `
                <li class="leaderboard-item">
                    <span class="rank ${idx === 0 ? 'top-1' : idx === 1 ? 'top-2' : idx === 2 ? 'top-3' : ''}">
                        ${idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : '#' + agent.rank}
                    </span>
                    <div class="agent-info">
                        <div class="agent-name">${agent.agent_name}</div>
                        <div class="agent-role">Level ${agent.level}</div>
                    </div>
                    <div class="agent-stats">
                        <span>⚡ ${agent.xp} XP</span>
                        <span>✅ ${agent.tasks_completed} Tasks</span>
                        <span>🎯 ${agent.accuracy}%</span>
                    </div>
                </li>
            `).join('');
        }
        
        function updateEventLog(events) {
            const log = document.getElementById('eventLog');
            
            if (events.length === 0) {
                log.innerHTML = '<p style="color: #aaa;">No events yet...</p>';
                return;
            }
            
            log.innerHTML = events.reverse().map(event => `
                <div class="event-item">
                    <span class="event-timestamp">${new Date(event.timestamp).toLocaleTimeString()}</span>
                    <span class="event-type">${event.type}</span>
                    ${event.data.agent_name ? ` - ${event.data.agent_name}` : ''}
                    ${event.data.success ? ' ✅' : ''}
                </div>
            `).join('');
        }
        
        async function addRandomAgent() {
            const roles = ['Code Reviewer', 'Bug Hunter', 'Performance Expert', 'Documentation Writer', 'Test Engineer'];
            const names = ['Codex', 'Bugsy', 'Optimizer', 'Docs', 'Testify', 'Phoenix', 'Sentinel'];
            
            const name = names[Math.floor(Math.random() * names.length)];
            const role = roles[Math.floor(Math.random() * roles.length)];
            
            try {
                const response = await fetch('/api/agents', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, role })
                });
                
                if (response.ok) {
                    updateDashboard();
                }
            } catch (error) {
                console.error('Error adding agent:', error);
            }
        }
        
        async function assignRandomTask() {
            try {
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                
                if (response.ok) {
                    updateDashboard();
                }
            } catch (error) {
                console.error('Error assigning task:', error);
            }
        }
        
        // Initial load and auto-refresh
        updateDashboard();
        setInterval(updateDashboard, 2000);
    </script>
</body>
</html>
"""


# ===================== API ROUTES =====================

@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/dashboard')
def get_dashboard():
    """Get current dashboard data"""
    return jsonify(ecosystem.get_dashboard_data())


@app.route('/api/agents', methods=['GET', 'POST'])
def manage_agents():
    """Get all agents or create a new agent"""
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name', f'Agent_{len(ecosystem.agents) + 1}')
        role = data.get('role', 'Developer')
        
        agent = ecosystem.create_agent(name, role)
        return jsonify(agent.to_dict()), 201
    
    return jsonify({aid: a.to_dict() for aid, a in ecosystem.agents.items()})


@app.route('/api/tasks', methods=['POST'])
def assign_task():
    """Assign a random task to a random agent"""
    if not ecosystem.agents:
        return jsonify({"error": "No agents available"}), 400
    
    import random
    agent_id = random.choice(list(ecosystem.agents.keys()))
    task_type = random.choice(list(TaskType))
    difficulty = random.randint(1, 5)
    
    task = ecosystem.assign_task(
        agent_id,
        task_type,
        f"Task: {task_type.value}",
        difficulty=difficulty
    )
    
    # Simulate completion after a short delay
    def complete_task():
        time.sleep(1)
        ecosystem.complete_task(
            task.id,
            success=True,
            metrics={
                "errors_caught": random.randint(0, 5),
                "lines_processed": random.randint(100, 500),
                "accuracy": random.randint(85, 100)
            }
        )
    
    thread = threading.Thread(target=complete_task, daemon=True)
    thread.start()
    
    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Mark a task as complete"""
    data = request.get_json() or {}
    success = data.get('success', True)
    metrics = data.get('metrics')
    
    agent = ecosystem.complete_task(task_id, success=success, metrics=metrics)
    return jsonify(agent.to_dict())


@app.route('/api/stats')
def get_stats():
    """Get overall ecosystem statistics"""
    return jsonify(ecosystem.get_ecosystem_stats())


@app.route('/api/leaderboard')
def get_leaderboard():
    """Get the leaderboard"""
    return jsonify(ecosystem.get_leaderboard())


# ===================== INITIALIZATION =====================

def initialize_demo():
    """Initialize with some demo agents and tasks"""
    demo_agents = [
        ("Codex", "Code Reviewer"),
        ("Bugsy", "Bug Hunter"),
        ("Optimizer", "Performance Tuner"),
    ]
    
    for name, role in demo_agents:
        ecosystem.create_agent(name, role)


if __name__ == '__main__':
    initialize_demo()
    print("🎮 Gamified Agent Ecosystem Dashboard")
    print("📊 Starting server at http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000, use_reloader=False)
