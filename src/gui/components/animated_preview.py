"""
Enhanced Preview Widget with animations and improved visual effects
"""

from PyQt6.QtWidgets import QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt6.QtGui import QColor
import os

class AnimatedPreviewWidget(QWidget):
    """Enhanced preview widget with animations and shadow effects"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "preview-area")
        
        # Setup shadow effect
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setColor(QColor(0, 0, 0, 60))
        self.shadow_effect.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow_effect)
        
        # Animation properties
        self._shadow_blur = 15
        self._shadow_offset_y = 4
        
        # Create animations
        self.hover_animation = QPropertyAnimation(self, b"shadowBlur")
        self.hover_animation.setDuration(200)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.offset_animation = QPropertyAnimation(self, b"shadowOffsetY")
        self.offset_animation.setDuration(200)
        self.offset_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    # Properties for animation
    @pyqtProperty(int)
    def shadowBlur(self):
        return self._shadow_blur
    
    @shadowBlur.setter
    def shadowBlur(self, value):
        self._shadow_blur = value
        self.shadow_effect.setBlurRadius(value)
    
    @pyqtProperty(int)
    def shadowOffsetY(self):
        return self._shadow_offset_y
    
    @shadowOffsetY.setter
    def shadowOffsetY(self, value):
        self._shadow_offset_y = value
        self.shadow_effect.setOffset(0, value)
    
    def enterEvent(self, event):
        """Animate on hover"""
        self.hover_animation.setStartValue(15)
        self.hover_animation.setEndValue(20)
        self.hover_animation.start()
        
        self.offset_animation.setStartValue(4)
        self.offset_animation.setEndValue(8)
        self.offset_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Animate on leave"""
        self.hover_animation.setStartValue(20)
        self.hover_animation.setEndValue(15)
        self.hover_animation.start()
        
        self.offset_animation.setStartValue(8)
        self.offset_animation.setEndValue(4)
        self.offset_animation.start()
        
        super().leaveEvent(event)

class AnimatedContentWidget(QWidget):
    """Content widget with subtle animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty("class", "preview-content")
        
        # Setup subtle shadow
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setBlurRadius(8)
        self.shadow_effect.setColor(QColor(0, 0, 0, 30))
        self.shadow_effect.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow_effect)
        
        # Animation properties
        self._shadow_blur = 8
        
        # Create animation
        self.hover_animation = QPropertyAnimation(self, b"shadowBlur")
        self.hover_animation.setDuration(150)
        self.hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    @pyqtProperty(int)
    def shadowBlur(self):
        return self._shadow_blur
    
    @shadowBlur.setter
    def shadowBlur(self, value):
        self._shadow_blur = value
        self.shadow_effect.setBlurRadius(value)
    
    def enterEvent(self, event):
        """Subtle animation on hover"""
        self.hover_animation.setStartValue(8)
        self.hover_animation.setEndValue(12)
        self.hover_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Subtle animation on leave"""
        self.hover_animation.setStartValue(12)
        self.hover_animation.setEndValue(8)
        self.hover_animation.start()
        super().leaveEvent(event)
