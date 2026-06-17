"""
Gamified Agent Ecosystem - A real-time monitoring system for managing agents
in an interactive, game-like environment with metrics, achievements, and visualization.
"""

import asyncio
import json
import time
from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from collections import defaultdict
import uuid


class AgentStatus(Enum):
    """Agent operational states"""
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    RESTING = "resting"
    COMPLETED = "completed"
    ERROR = "error"


class TaskType(Enum):
    """Types of tasks agents can perform"""
    CODE_REVIEW = "code_review"
    BUG_FIX = "bug_fix"
    FEATURE_BUILD = "feature_build"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    OPTIMIZATION = "optimization"


@dataclass
class Achievement:
    """Represents an agent achievement"""
    id: str
    name: str
    description: str
    icon: str
    points: int
    unlocked_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "points": self.points,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None,
            "unlocked": self.unlocked_at is not None
        }


@dataclass
class AgentStats:
    """Agent performance metrics"""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_xp: int = 0
    level: int = 1
    errors_caught: int = 0
    lines_processed: int = 0
    time_active: float = 0.0  # seconds
    accuracy_score: float = 100.0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Task:
    """A task in the ecosystem"""
    id: str
    type: TaskType
    agent_id: str
    status: AgentStatus
    description: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reward_xp: int = 100
    difficulty: int = 1  # 1-5
    
    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "reward_xp": self.reward_xp,
            "difficulty": self.difficulty
        }


@dataclass
class Agent:
    """A gamified agent in the ecosystem"""
    id: str
    name: str
    role: str
    status: AgentStatus = AgentStatus.IDLE
    stats: AgentStats = field(default_factory=AgentStats)
    achievements: Dict[str, Achievement] = field(default_factory=dict)
    current_task: Optional[Task] = None
    active_tasks: List[Task] = field(default_factory=list)
    last_action: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "stats": self.stats.to_dict(),
            "achievements": {k: v.to_dict() for k, v in self.achievements.items()},
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "active_tasks_count": len(self.active_tasks),
            "last_action": self.last_action.isoformat()
        }


class AchievementSystem:
    """Manages agent achievements and badges"""
    
    ACHIEVEMENTS = {
        "first_task": Achievement("first_task", "First Steps", "Completed first task", "👣", 10),
        "speed_demon": Achievement("speed_demon", "Speed Demon", "Completed 5 tasks in 1 hour", "⚡", 50),
        "perfectionist": Achievement("perfectionist", "Perfectionist", "100% accuracy on 10 tasks", "✨", 75),
        "bug_hunter": Achievement("bug_hunter", "Bug Hunter", "Found 10 bugs", "🐛", 60),
        "team_player": Achievement("team_player", "Team Player", "Coordinated with 5+ agents", "👥", 40),
        "marathon": Achievement("marathon", "Marathon Runner", "50 hours active time", "🏃", 100),
        "legendary": Achievement("legendary", "Legendary", "Reached level 10", "👑", 200),
    }
    
    def __init__(self):
        self.achievement_tracker: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def check_achievements(self, agent: Agent) -> List[Achievement]:
        """Check and unlock new achievements for an agent"""
        unlocked = []
        stats = agent.stats
        
        # First Task
        if stats.tasks_completed == 1 and "first_task" not in agent.achievements:
            ach = Achievement(**asdict(self.ACHIEVEMENTS["first_task"]))
            ach.unlocked_at = datetime.now()
            unlocked.append(ach)
        
        # Perfectionist
        if stats.accuracy_score == 100.0 and stats.tasks_completed >= 10:
            if "perfectionist" not in agent.achievements:
                ach = Achievement(**asdict(self.ACHIEVEMENTS["perfectionist"]))
                ach.unlocked_at = datetime.now()
                unlocked.append(ach)
        
        # Bug Hunter
        if stats.errors_caught >= 10 and "bug_hunter" not in agent.achievements:
            ach = Achievement(**asdict(self.ACHIEVEMENTS["bug_hunter"]))
            ach.unlocked_at = datetime.now()
            unlocked.append(ach)
        
        # Legendary
        if stats.level >= 10 and "legendary" not in agent.achievements:
            ach = Achievement(**asdict(self.ACHIEVEMENTS["legendary"]))
            ach.unlocked_at = datetime.now()
            unlocked.append(ach)
        
        return unlocked


class GameifiedAgentEcosystem:
    """Main ecosystem managing all agents and tasks"""
    
    def __init__(self, max_agents: int = 50):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.max_agents = max_agents
        self.achievement_system = AchievementSystem()
        self.event_history: List[Dict[str, Any]] = []
        self.leaderboard: List[tuple] = []
        self.start_time = datetime.now()
        
    def create_agent(self, name: str, role: str) -> Agent:
        """Create a new agent in the ecosystem"""
        agent = Agent(
            id=str(uuid.uuid4())[:8],
            name=name,
            role=role
        )
        self.agents[agent.id] = agent
        
        self._log_event("agent_created", {
            "agent_id": agent.id,
            "agent_name": name,
            "role": role
        })
        
        return agent
    
    def assign_task(self, agent_id: str, task_type: TaskType, 
                   description: str, difficulty: int = 1) -> Task:
        """Assign a task to an agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        task = Task(
            id=str(uuid.uuid4())[:8],
            type=task_type,
            agent_id=agent_id,
            status=AgentStatus.ACTIVE,
            description=description,
            created_at=datetime.now(),
            started_at=datetime.now(),
            difficulty=difficulty,
            reward_xp=100 * difficulty
        )
        
        self.tasks[task.id] = task
        agent.current_task = task
        agent.active_tasks.append(task)
        agent.status = AgentStatus.WORKING
        agent.last_action = datetime.now()
        
        self._log_event("task_assigned", {
            "agent_id": agent_id,
            "task_id": task.id,
            "task_type": task_type.value,
            "difficulty": difficulty
        })
        
        return task
    
    def complete_task(self, task_id: str, success: bool = True, 
                     metrics: Optional[Dict] = None) -> Agent:
        """Mark a task as completed"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        agent = self.agents[task.agent_id]
        
        task.status = AgentStatus.COMPLETED if success else AgentStatus.ERROR
        task.completed_at = datetime.now()
        
        # Update agent stats
        if success:
            agent.stats.tasks_completed += 1
            agent.stats.total_xp += task.reward_xp
            agent.stats.level = 1 + (agent.stats.total_xp // 500)
            
            if metrics:
                agent.stats.errors_caught += metrics.get("errors_caught", 0)
                agent.stats.lines_processed += metrics.get("lines_processed", 0)
                accuracy = metrics.get("accuracy", 100.0)
                # Update rolling accuracy
                total = agent.stats.tasks_completed
                agent.stats.accuracy_score = (
                    (agent.stats.accuracy_score * (total - 1) + accuracy) / total
                )
        else:
            agent.stats.tasks_failed += 1
        
        agent.status = AgentStatus.IDLE
        agent.current_task = None
        agent.last_action = datetime.now()
        
        # Check for achievements
        new_achievements = self.achievement_system.check_achievements(agent)
        for ach in new_achievements:
            agent.achievements[ach.id] = ach
            agent.stats.total_xp += ach.points
        
        # Remove from active tasks
        if task in agent.active_tasks:
            agent.active_tasks.remove(task)
        
        self._log_event("task_completed", {
            "agent_id": task.agent_id,
            "task_id": task_id,
            "success": success,
            "xp_earned": task.reward_xp,
            "new_level": agent.stats.level,
            "new_achievements": len(new_achievements)
        })
        
        return agent
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top agents by XP"""
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: (a.stats.total_xp, a.stats.tasks_completed),
            reverse=True
        )
        
        return [{
            "rank": i + 1,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "level": agent.stats.level,
            "xp": agent.stats.total_xp,
            "tasks_completed": agent.stats.tasks_completed,
            "accuracy": round(agent.stats.accuracy_score, 2)
        } for i, agent in enumerate(sorted_agents[:limit])]
    
    def get_ecosystem_stats(self) -> Dict:
        """Get overall ecosystem statistics"""
        total_xp = sum(a.stats.total_xp for a in self.agents.values())
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == AgentStatus.COMPLETED)
        
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.status == AgentStatus.WORKING),
            "total_xp": total_xp,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0,
            "uptime": self._calculate_uptime()
        }
    
    def _calculate_uptime(self) -> str:
        """Calculate ecosystem uptime"""
        delta = datetime.now() - self.start_time
        hours = delta.total_seconds() / 3600
        return f"{hours:.1f}h"
    
    def _log_event(self, event_type: str, data: Dict):
        """Log an event to history"""
        self.event_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        })
    
    def get_dashboard_data(self) -> Dict:
        """Get all data needed for the dashboard"""
        return {
            "timestamp": datetime.now().isoformat(),
            "ecosystem_stats": self.get_ecosystem_stats(),
            "leaderboard": self.get_leaderboard(),
            "agents": {aid: a.to_dict() for aid, a in self.agents.items()},
            "recent_events": self.event_history[-20:]
        }
    
    def export_state(self) -> str:
        """Export ecosystem state as JSON"""
        return json.dumps(self.get_dashboard_data(), indent=2)


# Example usage and simulation
async def simulate_agent_activity(ecosystem: GameifiedAgentEcosystem):
    """Simulate agent activity for demonstration"""
    
    # Create some agents
    agents = [
        ecosystem.create_agent("Codex", "Code Reviewer"),
        ecosystem.create_agent("Bugsy", "Bug Hunter"),
        ecosystem.create_agent("Docs", "Documentation Expert"),
        ecosystem.create_agent("Optimizer", "Performance Tuner"),
    ]
    
    # Simulate work
    for i in range(5):
        for agent in agents:
            task_types = list(TaskType)
            task_type = task_types[i % len(task_types)]
            
            task = ecosystem.assign_task(
                agent.id,
                task_type,
                f"Sample {task_type.value} task",
                difficulty=min(5, 1 + (i % 3))
            )
            
            # Simulate task completion
            await asyncio.sleep(0.1)
            ecosystem.complete_task(
                task.id,
                success=True,
                metrics={
                    "errors_caught": 2 + i,
                    "lines_processed": 150 + i * 50,
                    "accuracy": 95 + (i % 5)
                }
            )
    
    return ecosystem


if __name__ == "__main__":
    # Create and display the ecosystem
    ecosystem = GameifiedAgentEcosystem()
    
    # Run simulation
    asyncio.run(simulate_agent_activity(ecosystem))
    
    # Display dashboard
    print("=" * 80)
    print("🎮 GAMIFIED AGENT ECOSYSTEM DASHBOARD 🎮")
    print("=" * 80)
    print(ecosystem.export_state())
