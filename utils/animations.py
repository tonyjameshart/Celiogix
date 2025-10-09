#!/usr/bin/env python3
"""
Animation and transition utilities for enhanced visual feedback
"""

from typing import Any, Dict, List, Optional, Callable, Union
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsEffect
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QTimer, QSequentialAnimationGroup,
    QParallelAnimationGroup, QAbstractAnimation, Signal, QObject
)
from PySide6.QtGui import QPainter, QColor, QPen, QBrush
from enum import Enum


class AnimationType(Enum):
    """Animation types"""
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_IN = "slide_in"
    SLIDE_OUT = "slide_out"
    SCALE_IN = "scale_in"
    SCALE_OUT = "scale_out"
    BOUNCE = "bounce"
    SHAKE = "shake"
    PULSE = "pulse"
    ROTATE = "rotate"


class AnimationManager(QObject):
    """Centralized animation manager"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running_animations = []
        self.animation_queue = []
    
    def create_fade_animation(self, widget: QWidget, duration: int = 300, 
                            start_opacity: float = 0.0, end_opacity: float = 1.0) -> QPropertyAnimation:
        """Create fade animation for widget"""
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        return animation
    
    def create_slide_animation(self, widget: QWidget, direction: str = "right", 
                             duration: int = 300) -> QPropertyAnimation:
        """Create slide animation for widget"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Get current geometry
        current_rect = widget.geometry()
        
        # Calculate start and end positions based on direction
        if direction == "right":
            start_rect = current_rect.translated(-current_rect.width(), 0)
            end_rect = current_rect
        elif direction == "left":
            start_rect = current_rect.translated(current_rect.width(), 0)
            end_rect = current_rect
        elif direction == "up":
            start_rect = current_rect.translated(0, current_rect.height())
            end_rect = current_rect
        elif direction == "down":
            start_rect = current_rect.translated(0, -current_rect.height())
            end_rect = current_rect
        else:
            start_rect = end_rect = current_rect
        
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        
        return animation
    
    def create_scale_animation(self, widget: QWidget, start_scale: float = 0.0, 
                             end_scale: float = 1.0, duration: int = 300) -> QPropertyAnimation:
        """Create scale animation for widget"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutBack)
        
        # Get current geometry
        current_rect = widget.geometry()
        center_x = current_rect.center().x()
        center_y = current_rect.center().y()
        
        # Calculate scaled rectangles
        start_width = int(current_rect.width() * start_scale)
        start_height = int(current_rect.height() * start_scale)
        end_width = int(current_rect.width() * end_scale)
        end_height = int(current_rect.height() * end_scale)
        
        start_rect = QRect(
            center_x - start_width // 2,
            center_y - start_height // 2,
            start_width,
            start_height
        )
        
        end_rect = QRect(
            center_x - end_width // 2,
            center_y - end_height // 2,
            end_width,
            end_height
        )
        
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        
        return animation
    
    def create_bounce_animation(self, widget: QWidget, duration: int = 600) -> QSequentialAnimationGroup:
        """Create bounce animation for widget"""
        group = QSequentialAnimationGroup()
        
        # Scale up
        scale_up = self.create_scale_animation(widget, 1.0, 1.2, duration // 3)
        scale_up.setEasingCurve(QEasingCurve.OutCubic)
        
        # Scale down
        scale_down = self.create_scale_animation(widget, 1.2, 0.9, duration // 3)
        scale_down.setEasingCurve(QEasingCurve.InCubic)
        
        # Scale back to normal
        scale_normal = self.create_scale_animation(widget, 0.9, 1.0, duration // 3)
        scale_normal.setEasingCurve(QEasingCurve.OutCubic)
        
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        group.addAnimation(scale_normal)
        
        return group
    
    def create_shake_animation(self, widget: QWidget, duration: int = 500) -> QSequentialAnimationGroup:
        """Create shake animation for widget"""
        group = QSequentialAnimationGroup()
        
        # Get current position
        current_pos = widget.pos()
        
        # Create shake movements
        shake_distance = 10
        shake_duration = duration // 10
        
        for i in range(5):
            # Move right
            move_right = QPropertyAnimation(widget, b"pos")
            move_right.setDuration(shake_duration)
            move_right.setStartValue(current_pos)
            move_right.setEndValue(current_pos + QPoint(shake_distance, 0))
            move_right.setEasingCurve(QEasingCurve.Linear)
            
            # Move left
            move_left = QPropertyAnimation(widget, b"pos")
            move_left.setDuration(shake_duration)
            move_left.setStartValue(current_pos + QPoint(shake_distance, 0))
            move_left.setEndValue(current_pos - QPoint(shake_distance, 0))
            move_left.setEasingCurve(QEasingCurve.Linear)
            
            group.addAnimation(move_right)
            group.addAnimation(move_left)
            
            current_pos = current_pos - QPoint(shake_distance, 0)
            shake_distance = int(shake_distance * 0.8)  # Decrease shake intensity
        
        # Return to original position
        return_home = QPropertyAnimation(widget, b"pos")
        return_home.setDuration(shake_duration)
        return_home.setStartValue(current_pos)
        return_home.setEndValue(widget.pos())
        return_home.setEasingCurve(QEasingCurve.OutCubic)
        
        group.addAnimation(return_home)
        
        return group
    
    def create_pulse_animation(self, widget: QWidget, duration: int = 1000) -> QSequentialAnimationGroup:
        """Create pulse animation for widget"""
        group = QSequentialAnimationGroup()
        
        # Scale up
        scale_up = self.create_scale_animation(widget, 1.0, 1.1, duration // 2)
        scale_up.setEasingCurve(QEasingCurve.InOutCubic)
        
        # Scale down
        scale_down = self.create_scale_animation(widget, 1.1, 1.0, duration // 2)
        scale_down.setEasingCurve(QEasingCurve.InOutCubic)
        
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        
        return group
    
    def create_rotate_animation(self, widget: QWidget, degrees: float = 360, 
                              duration: int = 1000) -> QPropertyAnimation:
        """Create rotate animation for widget"""
        # This would require a custom property or using QGraphicsEffect
        # For now, we'll create a simple implementation
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        
        # Simple rotation simulation by changing geometry
        current_rect = widget.geometry()
        animation.setStartValue(current_rect)
        animation.setEndValue(current_rect)  # Placeholder
        
        return animation
    
    def play_animation(self, animation: QAbstractAnimation, 
                      on_finished: Optional[Callable] = None) -> QAbstractAnimation:
        """Play animation with optional callback"""
        if on_finished:
            animation.finished.connect(on_finished)
        
        animation.start()
        self.running_animations.append(animation)
        
        # Remove from running list when finished
        animation.finished.connect(lambda: self.running_animations.remove(animation))
        
        return animation
    
    def stop_all_animations(self):
        """Stop all running animations"""
        for animation in self.running_animations:
            animation.stop()
        self.running_animations.clear()
    
    def create_sequence(self, animations: List[QAbstractAnimation]) -> QSequentialAnimationGroup:
        """Create sequential animation group"""
        group = QSequentialAnimationGroup()
        for animation in animations:
            group.addAnimation(animation)
        return group
    
    def create_parallel(self, animations: List[QAbstractAnimation]) -> QParallelAnimationGroup:
        """Create parallel animation group"""
        group = QParallelAnimationGroup()
        for animation in animations:
            group.addAnimation(animation)
        return group


class AnimatedWidget(QWidget):
    """Base class for animated widgets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_manager = AnimationManager(self)
        self.current_animation = None
    
    def fade_in(self, duration: int = 300, callback: Optional[Callable] = None):
        """Fade in animation"""
        animation = self.animation_manager.create_fade_animation(
            self, duration, 0.0, 1.0
        )
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def fade_out(self, duration: int = 300, callback: Optional[Callable] = None):
        """Fade out animation"""
        animation = self.animation_manager.create_fade_animation(
            self, duration, 1.0, 0.0
        )
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def slide_in(self, direction: str = "right", duration: int = 300, 
                callback: Optional[Callable] = None):
        """Slide in animation"""
        animation = self.animation_manager.create_slide_animation(
            self, direction, duration
        )
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def slide_out(self, direction: str = "right", duration: int = 300, 
                 callback: Optional[Callable] = None):
        """Slide out animation"""
        # Reverse the direction for slide out
        reverse_directions = {
            "right": "left",
            "left": "right",
            "up": "down",
            "down": "up"
        }
        reverse_direction = reverse_directions.get(direction, direction)
        
        animation = self.animation_manager.create_slide_animation(
            self, reverse_direction, duration
        )
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def scale_in(self, duration: int = 300, callback: Optional[Callable] = None):
        """Scale in animation"""
        animation = self.animation_manager.create_scale_animation(
            self, 0.0, 1.0, duration
        )
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def scale_out(self, duration: int = 300, callback: Optional[Callable] = None):
        """Scale out animation"""
        animation = self.animation_manager.create_scale_animation(
            self, 1.0, 0.0, duration
        )
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def bounce(self, duration: int = 600, callback: Optional[Callable] = None):
        """Bounce animation"""
        animation = self.animation_manager.create_bounce_animation(self, duration)
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def shake(self, duration: int = 500, callback: Optional[Callable] = None):
        """Shake animation"""
        animation = self.animation_manager.create_shake_animation(self, duration)
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def pulse(self, duration: int = 1000, callback: Optional[Callable] = None):
        """Pulse animation"""
        animation = self.animation_manager.create_pulse_animation(self, duration)
        self.current_animation = animation
        self.animation_manager.play_animation(animation, callback)
    
    def stop_animation(self):
        """Stop current animation"""
        if self.current_animation:
            self.current_animation.stop()
            self.current_animation = None


class LoadingSpinner(QWidget):
    """Animated loading spinner"""
    
    def __init__(self, parent=None, size: int = 40):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_angle)
        
        self.setFixedSize(size, size)
    
    def start_animation(self):
        """Start spinner animation"""
        self.timer.start(50)  # Update every 50ms
    
    def stop_animation(self):
        """Stop spinner animation"""
        self.timer.stop()
    
    def update_angle(self):
        """Update rotation angle"""
        self.angle = (self.angle + 10) % 360
        self.update()
    
    def paintEvent(self, event):
        """Paint spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up pen
        pen = QPen(QColor("#3498db"))
        pen.setWidth(3)
        pen.setCapStyle(QPen.RoundCap)
        painter.setPen(pen)
        
        # Draw spinner
        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 5
        
        for i in range(8):
            angle = (self.angle + i * 45) % 360
            alpha = int(255 * (1 - i / 8))
            
            pen.setColor(QColor(52, 152, 219, alpha))
            painter.setPen(pen)
            
            start_angle = angle * 16  # Qt uses 1/16th degrees
            span_angle = 30 * 16
            
            painter.drawArc(
                center.x() - radius, center.y() - radius,
                radius * 2, radius * 2,
                start_angle, span_angle
            )


class ProgressBar(QWidget):
    """Animated progress bar"""
    
    # Signals
    progress_changed = Signal(int)
    
    def __init__(self, parent=None, maximum: int = 100):
        super().__init__(parent)
        self.maximum = maximum
        self.value = 0
        self.animation_duration = 300
        self.current_animation = None
        
        self.setFixedHeight(8)
        self.setMinimumWidth(200)
    
    def set_value(self, value: int, animated: bool = True):
        """Set progress value with optional animation"""
        if not animated:
            self.value = min(max(value, 0), self.maximum)
            self.update()
            self.progress_changed.emit(self.value)
            return
        
        # Animate progress change
        start_value = self.value
        end_value = min(max(value, 0), self.maximum)
        
        if start_value == end_value:
            return
        
        # Create animation
        animation = QPropertyAnimation(self, b"value")
        animation.setDuration(self.animation_duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        animation.valueChanged.connect(self._on_value_changed)
        animation.finished.connect(self._on_animation_finished)
        
        self.current_animation = animation
        animation.start()
    
    def _on_value_changed(self, value):
        """Handle animation value change"""
        self.value = int(value)
        self.update()
        self.progress_changed.emit(self.value)
    
    def _on_animation_finished(self):
        """Handle animation finished"""
        self.current_animation = None
    
    def paintEvent(self, event):
        """Paint progress bar"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        bg_rect = self.rect()
        painter.fillRect(bg_rect, QColor("#ecf0f1"))
        
        # Progress
        if self.value > 0:
            progress_width = int((self.value / self.maximum) * self.width())
            progress_rect = QRect(0, 0, progress_width, self.height())
            painter.fillRect(progress_rect, QColor("#3498db"))


# Global animation manager instance
animation_manager = AnimationManager()


def get_animation_manager() -> AnimationManager:
    """Get global animation manager"""
    return animation_manager


def animate_widget(widget: QWidget, animation_type: AnimationType, 
                  duration: int = 300, callback: Optional[Callable] = None):
    """Convenience function to animate any widget"""
    manager = get_animation_manager()
    
    if animation_type == AnimationType.FADE_IN:
        animation = manager.create_fade_animation(widget, duration, 0.0, 1.0)
    elif animation_type == AnimationType.FADE_OUT:
        animation = manager.create_fade_animation(widget, duration, 1.0, 0.0)
    elif animation_type == AnimationType.SLIDE_IN:
        animation = manager.create_slide_animation(widget, "right", duration)
    elif animation_type == AnimationType.SLIDE_OUT:
        animation = manager.create_slide_animation(widget, "left", duration)
    elif animation_type == AnimationType.SCALE_IN:
        animation = manager.create_scale_animation(widget, 0.0, 1.0, duration)
    elif animation_type == AnimationType.SCALE_OUT:
        animation = manager.create_scale_animation(widget, 1.0, 0.0, duration)
    elif animation_type == AnimationType.BOUNCE:
        animation = manager.create_bounce_animation(widget, duration)
    elif animation_type == AnimationType.SHAKE:
        animation = manager.create_shake_animation(widget, duration)
    elif animation_type == AnimationType.PULSE:
        animation = manager.create_pulse_animation(widget, duration)
    else:
        return None
    
    return manager.play_animation(animation, callback)
