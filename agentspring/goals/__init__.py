"""
Goals module for AgentSpring.

This module provides the Goal class and related components for defining
and tracking goals within the AgentSpring framework.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class GoalStatus(str, Enum):
    """Status of a goal."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Goal(BaseModel):
    """
    Represents a goal that an agent can work towards.
    
    A goal can have subgoals, allowing for hierarchical goal structures.
    """
    id: str = Field(default_factory=lambda: f"goal_{datetime.now().timestamp()}")
    description: str
    status: GoalStatus = GoalStatus.PENDING
    progress: float = 0.0  # 0.0 to 1.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_id: Optional[str] = None
    subgoals: List['Goal'] = Field(default_factory=list)
    success_criteria: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_subgoal(self, goal: 'Goal') -> None:
        """Add a subgoal to this goal."""
        goal.parent_id = self.id
        self.subgoals.append(goal)
    
    def update_progress(self, progress: float, metadata: Optional[Dict] = None) -> None:
        """
        Update the progress of this goal.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            metadata: Optional metadata to include with the update
        """
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.utcnow()
        
        if metadata:
            self.metadata.update(metadata)
            
        # Update status based on progress
        if self.progress >= 1.0:
            self.status = GoalStatus.COMPLETED
        elif self.progress > 0.0:
            self.status = GoalStatus.IN_PROGRESS
    
    def is_completed(self) -> bool:
        """Check if this goal and all its subgoals are completed."""
        if self.status == GoalStatus.COMPLETED:
            return True
            
        if not self.subgoals:
            return self.status == GoalStatus.COMPLETED
            
        return all(subgoal.is_completed() for subgoal in self.subgoals)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the goal to a dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "parent_id": self.parent_id,
            "subgoals": [subgoal.to_dict() for subgoal in self.subgoals],
            "success_criteria": self.success_criteria
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        """Create a goal from a dictionary."""
        # Handle string status
        if isinstance(data.get('status'), str):
            data['status'] = GoalStatus(data['status'])
            
        # Convert string timestamps to datetime objects
        for time_field in ['created_at', 'updated_at']:
            if time_field in data and isinstance(data[time_field], str):
                data[time_field] = datetime.fromisoformat(data[time_field])
        
        # Handle subgoals recursively
        subgoals_data = data.pop('subgoals', [])
        goal = cls(**data)
        
        for subgoal_data in subgoals_data:
            goal.add_subgoal(cls.from_dict(subgoal_data))
            
        return goal