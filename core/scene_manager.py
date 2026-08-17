# 场景管理器：统一场景栈管理、转场动画、资源清理
# 避免直接使用 game.set_scene，提供 push/pop/replace 语义
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
import pygame

if TYPE_CHECKING:
    from core.main import Game

# 场景转场类型
TRANSITION_NONE = 0
TRANSITION_FADE = 1
TRANSITION_SLIDE = 2


class SceneManager:
    """场景栈管理器：支持 push/pop/replace，自动处理资源清理和转场"""
    
    def __init__(self, game: "Game"):
        self.game = game
        self._stack: list = []          # 场景栈：[bottom, ..., top]
        self._transition = TRANSITION_NONE
        self._transition_t = 0.0
        self._transition_duration = 0.3
        self._next_scene = None
        self._pop_count = 0
        self._replace_flag = False
    
    @property
    def current(self) -> Optional[object]:
        return self._stack[-1] if self._stack else None
    
    @property
    def depth(self) -> int:
        return len(self._stack)
    
    def push(self, scene, transition: int = TRANSITION_FADE, duration: float = 0.3):
        """压入新场景（保留当前场景，可返回）"""
        if self.current:
            self.current.on_pause()
        self._transition = transition
        self._transition_duration = duration
        self._transition_t = 0.0
        self._next_scene = scene
        self._replace_flag = False
        self._pop_count = 0
    
    def replace(self, scene, transition: int = TRANSITION_FADE, duration: float = 0.3):
        """替换当前场景（销毁当前场景）"""
        if self.current:
            self.current.on_destroy()
            self._stack.pop()
        self._transition = transition
        self._transition_duration = duration
        self._transition_t = 0.0
        self._next_scene = scene
        self._replace_flag = True
        self._pop_count = 0
    
    def pop(self, count: int = 1, transition: int = TRANSITION_FADE, duration: float = 0.3):
        """弹出场景（返回上一场景）"""
        if len(self._stack) <= count:
            return  # 不能弹出根场景
        self._transition = transition
        self._transition_duration = duration
        self._transition_t = 0.0
        self._next_scene = None
        self._replace_flag = False
        self._pop_count = count
    
    def pop_to_root(self, transition: int = TRANSITION_FADE, duration: float = 0.3):
        """弹出到根场景（主菜单）"""
        self.pop(len(self._stack) - 1, transition, duration)
    
    def update(self, dt: float):
        """更新转场动画"""
        if self._transition_t < self._transition_duration:
            self._transition_t += dt
            return
        
        # 转场完成，执行场景切换
        if self._pop_count > 0:
            for _ in range(min(self._pop_count, len(self._stack))):
                if self._stack:
                    self._stack[-1].on_destroy()
                    self._stack.pop()
            self._pop_count = 0
        
        if self._next_scene:
            self._next_scene.game = self.game
            self._stack.append(self._next_scene)
            self._next_scene.on_enter()
            self._next_scene = None
        
        self._transition = TRANSITION_NONE
    
    def draw(self, surf: pygame.Surface):
        """绘制场景栈（支持转场叠加）"""
        if not self._stack:
            return
        
        # 简单实现：只绘制栈顶场景
        # 高级实现可绘制多层并应用转场效果
        top = self._stack[-1]
        if hasattr(top, 'draw'):
            top.draw(surf)
    
    def handle_event(self, event):
        """事件分发给栈顶场景"""
        if self.current and hasattr(self.current, 'event'):
            self.current.event(event)


# 全局场景管理器实例（在 Game.__init__ 中初始化）
_scene_manager: Optional[SceneManager] = None

def get_scene_manager() -> Optional[SceneManager]:
    return _scene_manager

def set_scene_manager(mgr: SceneManager):
    global _scene_manager
    _scene_manager = mgr