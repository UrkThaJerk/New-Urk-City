# 🎮 Gamified Agent Ecosystem - Setup Guide

A real-time monitoring system for managing agents in an interactive, game-like environment with metrics, achievements, and visualization.

## 📋 Features

### Core System (`src/agent_ecosystem.py`)
- **Agent Management**: Create and manage multiple agents with unique identities
- **Task System**: Assign diverse task types with difficulty levels
- **XP & Leveling**: Dynamic progression system
- **Achievement Badges**: Unlock achievements like Bug Hunter, Perfectionist, Legendary
- **Performance Metrics**: Track accuracy, errors caught, lines processed
- **Event Logging**: Complete history of all ecosystem events
- **Leaderboard**: Real-time ranking by XP and task completion

### Web Dashboard (`src/dashboard.py`)
- **Live Statistics**: Active agents, total XP, tasks completed, success rate
- **Agent Grid**: Individual agent cards with status, level, achievements
- **Interactive Leaderboard**: Top performers with medals and rankings
- **Event Stream**: Real-time activity log
- **One-Click Controls**: Add agents and assign tasks instantly
- **Auto-Refresh**: Updates every 2 seconds
- **Gaming UI**: Modern design with gradients, animations, and emojis

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Dashboard

```bash
python src/dashboard.py
```

You'll see:
```
🎮 Gamified Agent Ecosystem Dashboard
📊 Starting server at http://localhost:5000
============================================================
```

### 3. Open in Browser

Navigate to: **http://localhost:5000**

## 🎮 How to Use

### Create Agents
Click the **"+ Add Agent"** button to create a new agent with a random name and role.

**Available Roles**:
- Code Reviewer
- Bug Hunter
- Performance Expert
- Documentation Writer
- Test Engineer

### Assign Tasks
Click the **"⚡ Assign Random Task"** button to assign tasks to agents.

**Available Task Types**:
- Code Review
- Bug Fix
- Feature Building
- Documentation
- Testing
- Optimization

### Watch Real-Time Activity
- **Agent Cards**: Display current status, level, XP, accuracy, and achievements
- **Leaderboard**: Ranked by XP and task completion (with 🥇🥈🥉 medals)
- **Event Log**: Every action timestamped and logged
- **Stats Dashboard**: Overall ecosystem metrics

## 📊 Metrics Explained

### Per Agent
- **Level**: Starts at 1, increases per 500 XP earned
- **XP**: Earned from completing tasks (100 × difficulty)
- **Tasks Completed**: Total successful task count
- **Accuracy**: Percentage of successful completions
- **Achievements**: Unlocked badges showing milestones

### Ecosystem
- **Active Agents**: Currently working on tasks
- **Total XP**: Combined XP from all agents
- **Tasks Completed**: Total completed across all agents
- **Success Rate**: Percentage of successful task completions

## 🏆 Achievement System

| Badge | Name | Requirement | Reward |
|-------|------|-------------|--------|
| 👣 | First Steps | Complete first task | 10 XP |
| ⚡ | Speed Demon | 5 tasks in 1 hour | 50 XP |
| ✨ | Perfectionist | 100% accuracy on 10 tasks | 75 XP |
| 🐛 | Bug Hunter | Find 10 bugs | 60 XP |
| 👥 | Team Player | Coordinate with 5+ agents | 40 XP |
| 🏃 | Marathon Runner | 50 hours active time | 100 XP |
| 👑 | Legendary | Reach level 10 | 200 XP |

## 🔧 API Endpoints

### Dashboard
- `GET /` - Main dashboard UI
- `GET /api/dashboard` - Full dashboard data (JSON)

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
  ```json
  {
    "name": "CustomName",
    "role": "Custom Role"
  }
  ```

### Tasks
- `POST /api/tasks` - Assign random task to random agent
- `POST /api/tasks/<task_id>/complete` - Complete a task
  ```json
  {
    "success": true,
    "metrics": {
      "errors_caught": 3,
      "lines_processed": 250,
      "accuracy": 98.5
    }
  }
  ```

### Stats
- `GET /api/stats` - Ecosystem statistics
- `GET /api/leaderboard` - Leaderboard data

## 💡 Example Usage

### Python Integration

```python
from agent_ecosystem import GameifiedAgentEcosystem, TaskType
import asyncio

# Create ecosystem
ecosystem = GameifiedAgentEcosystem()

# Create agents
agent1 = ecosystem.create_agent("Aurora", "Code Reviewer")
agent2 = ecosystem.create_agent("Nova", "Bug Hunter")

# Assign tasks
task = ecosystem.assign_task(
    agent1.id,
    TaskType.CODE_REVIEW,
    "Review new authentication module",
    difficulty=3
)

# Complete task with metrics
ecosystem.complete_task(
    task.id,
    success=True,
    metrics={
        "errors_caught": 2,
        "lines_processed": 340,
        "accuracy": 98.0
    }
)

# Get leaderboard
leaderboard = ecosystem.get_leaderboard(limit=10)
print(leaderboard)

# Export state
state = ecosystem.export_state()
print(state)
```

## 🎨 Customization

### Modify Achievement Conditions
Edit `src/agent_ecosystem.py` in the `AchievementSystem.check_achievements()` method:

```python
# Example: Change Bug Hunter requirement
if stats.errors_caught >= 5:  # Changed from 10
    # Unlock achievement
```

### Change XP Rewards
Modify task reward multiplier in `assign_task()` method:

```python
reward_xp = 200 * difficulty  # Changed from 100
```

### Customize Leveling
Edit the level calculation in `complete_task()`:

```python
agent.stats.level = 1 + (agent.stats.total_xp // 300)  # Changed from 500
```

## 📁 Project Structure

```
New-Urk-City/
├── src/
│   ├── agent_ecosystem.py    # Core system
│   └── dashboard.py           # Web interface
├── tests/                     # Unit tests (future)
├── requirements.txt           # Dependencies
├── SETUP.md                   # This file
└── README.md                  # Project overview
```

## 🐛 Troubleshooting

### Port Already in Use

If port 5000 is in use, edit `src/dashboard.py`:

```python
app.run(debug=True, port=8000, use_reloader=False)  # Change port
```

### Dashboard Not Updating

1. Check browser console (F12) for errors
2. Ensure Flask server is running
3. Clear browser cache (Ctrl+Shift+Delete)

### Import Errors

Make sure you're running from the project root:

```bash
cd New-Urk-City
python src/dashboard.py
```

## 📈 Future Enhancements

- [ ] Persistent database storage (SQLite/PostgreSQL)
- [ ] Agent personality traits
- [ ] Team-based competitions
- [ ] Time-based challenges
- [ ] Performance analytics
- [ ] Export leaderboard as CSV
- [ ] WebSocket for real-time updates
- [ ] Mobile responsive improvements
- [ ] Dark/Light theme toggle
- [ ] Agent retirement/legacy system

## 📝 License

This project is part of New-Urk-City repository.

---

**Happy agent managing! 🎮⚡**
