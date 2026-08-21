import json
import time
import threading
import pickle
from collections import defaultdict
from typing import Dict, List, Tuple
import numpy as np
from src.actions import execute_action_safe
from src.vision import capture_and_prepare_screen

class ImitationLearning:
    """
    5 режимов:
    1. Запись (учусь у тебя)
    2. Self-play (учусь сам)
    3. Клон (играю как ты)
    4. Обычный (без обучения)
    5. Свободный (играю как хочу)
    """
    
    def __init__(self, agent):
        self.agent = agent
        self.is_recording = False
        self.is_playing = False
        self.is_cloning = False
        self.is_free = False
        
        self.action_history = []
        self.action_sequences = []
        self.patterns = defaultdict(list)
        self.free_actions = []
        
        self.total_actions_recorded = 0
        self.total_actions_played = 0
        self.total_free_actions = 0
        self.match_score = 0.0
        self.free_score = 0.0
        
        self.thread = None
        self.running = False
        
        self.load_data()
    
    def start_recording(self):
        if self.is_recording:
            return
        self._stop_all_internal()
        self.is_recording = True
        self.running = True
        
        self.thread = threading.Thread(target=self._record_loop)
        self.thread.daemon = True
        self.thread.start()
        
        return "🎮 Режим 1: Запись начата! Играй, я учусь твоему стилю!"
    
    def start_self_learning(self):
        if self.is_playing:
            return
        self._stop_all_internal()
        self.is_playing = True
        self.running = True
        
        self.thread = threading.Thread(target=self._self_play_loop)
        self.thread.daemon = True
        self.thread.start()
        
        return "🤖 Режим 2: ИИ играет и учится сам!"
    
    def start_cloning(self):
        if self.is_cloning:
            return
        
        if len(self.action_history) < 10:
            return "❌ Недостаточно данных! Сначала поиграй в режиме 1."
        
        self._stop_all_internal()
        self.is_cloning = True
        self.running = True
        
        self.thread = threading.Thread(target=self._clone_loop)
        self.thread.daemon = True
        self.thread.start()
        
        return "🧠 Режим 3: Клон активирован! Я играю как ты!"
    
    def stop_all(self):
        self._stop_all_internal()
        return "⏸️ Режим 4: Обычный режим. Играй спокойно, я не мешаю."
    
    def start_free_mode(self):
        if self.is_free:
            return
        
        self._stop_all_internal()
        self.is_free = True
        self.running = True
        
        self.thread = threading.Thread(target=self._free_loop)
        self.thread.daemon = True
        self.thread.start()
        
        return "🔥 Режим 5: Свободный режим! ИИ играет как хочет!"
    
    def _stop_all_internal(self):
        self.running = False
        self.is_recording = False
        self.is_playing = False
        self.is_cloning = False
        self.is_free = False
        
        if self.thread:
            self.thread.join(timeout=2)
        
        self.save_data()
    
    def _record_loop(self):
        last_action_time = time.time()
        
        while self.running and self.is_recording:
            try:
                state = self._get_game_state()
                actions = self._capture_player_actions()
                
                if actions:
                    self.action_history.append({
                        "timestamp": time.time(),
                        "state": state,
                        "actions": actions,
                        "reward": self._calculate_reward(state)
                    })
                    self.total_actions_recorded += 1
                    
                    state_key = self._state_to_key(state)
                    self.patterns[state_key].append(actions)
                
                if time.time() - last_action_time > 10:
                    self.save_data()
                    last_action_time = time.time()
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Ошибка записи: {e}")
                time.sleep(0.5)
    
    def _self_play_loop(self):
        while self.running and self.is_playing:
            try:
                state = self._get_game_state()
                
                if np.random.random() < 0.3:
                    action = self._explore_action()
                else:
                    action = self._best_action_for_state(state)
                
                result = execute_action_safe(action)
                reward = self._calculate_reward(state)
                
                if reward > 0:
                    self.action_history.append({
                        "timestamp": time.time(),
                        "state": state,
                        "actions": [action],
                        "reward": reward
                    })
                    self.total_actions_played += 1
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Ошибка self-play: {e}")
                time.sleep(0.5)
    
    def _clone_loop(self):
        if not self.action_history:
            return
        
        self._analyze_patterns()
        
        while self.running and self.is_cloning:
            try:
                state = self._get_game_state()
                state_key = self._state_to_key(state)
                
                if state_key in self.patterns and self.patterns[state_key]:
                    actions = max(self.patterns[state_key], key=self.patterns[state_key].count)
                    
                    if np.random.random() < 0.8:
                        for action in actions:
                            execute_action_safe(action)
                    else:
                        variation = self._add_variation(actions)
                        for action in variation:
                            execute_action_safe(action)
                    
                    self.total_actions_played += 1
                    self.match_score = min(100, self.match_score + 0.1)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Ошибка клонирования: {e}")
                time.sleep(0.5)
    
    def _free_loop(self):
        print("🔥 Свободный режим активирован! ИИ играет как хочет...")
        
        while self.running and self.is_free:
            try:
                state = self._get_game_state()
                action = self._free_will_action(state)
                
                result = execute_action_safe(action)
                reward = self._calculate_reward(state)
                
                if reward > 0:
                    self.free_actions.append({
                        "timestamp": time.time(),
                        "state": state,
                        "action": action,
                        "reward": reward
                    })
                    self.total_free_actions += 1
                    self.free_score = min(100, self.free_score + 0.05)
                
                elif reward < -2:
                    self._learn_from_failure(state, action)
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Ошибка свободного режима: {e}")
                time.sleep(0.5)
    
    def _free_will_action(self, state: Dict) -> Dict:
        rand = np.random.random()
        
        if rand < 0.4:
            return self._best_action_for_state(state)
        elif rand < 0.7:
            return self._logical_random_action(state)
        elif rand < 0.9:
            return self._intuitive_action(state)
        else:
            return self._experimental_action()
    
    def _logical_random_action(self, state: Dict) -> Dict:
        actions = []
        
        if state.get("enemies_near", 0) > 2:
            actions = [
                {"type": "press", "key": "space"},
                {"type": "press", "key": "shift"},
                {"type": "press", "key": "f"},
                {"type": "click", "x": np.random.randint(0, 1920), "y": np.random.randint(0, 1080)}
            ]
        elif state.get("safe_zone_near", False):
            actions = [
                {"type": "press", "key": "w"},
                {"type": "press", "key": "shift"},
            ]
        else:
            actions = [
                {"type": "press", "key": "w"},
                {"type": "press", "key": "a"},
                {"type": "press", "key": "s"},
                {"type": "press", "key": "d"},
                {"type": "move", "x": np.random.randint(0, 1920), "y": np.random.randint(0, 1080)}
            ]
        
        return np.random.choice(actions)
    
    def _intuitive_action(self, state: Dict) -> Dict:
        state_key = self._state_to_key(state)
        
        if state_key in self.patterns and self.patterns[state_key]:
            actions = self.patterns[state_key]
            return np.random.choice(actions)[0] if actions else {"type": "idle"}
        
        if self.free_actions:
            last_free = self.free_actions[-1]
            return last_free["action"]
        
        return {"type": "idle"}
    
    def _experimental_action(self) -> Dict:
        experimental_actions = [
            {"type": "hotkey", "keys": ["ctrl", "shift", "e"]},
            {"type": "press", "key": "tab"},
            {"type": "press", "key": "esc"},
            {"type": "move", "x": np.random.randint(0, 1920), "y": np.random.randint(0, 1080), "duration": 1.0},
            {"type": "click", "x": np.random.randint(0, 1920), "y": np.random.randint(0, 1080), "button": "right"},
            {"type": "type", "text": "hello world"},
            {"type": "scroll", "amount": np.random.randint(-10, 10)},
        ]
        return np.random.choice(experimental_actions)
    
    def _learn_from_failure(self, state: Dict, action: Dict):
        state_key = self._state_to_key(state)
        if state_key in self.patterns:
            self.patterns[state_key] = [
                a for a in self.patterns[state_key] 
                if a != [action]
            ]
    
    def _get_game_state(self) -> Dict:
        return {
            "health": np.random.randint(0, 100),
            "position": (np.random.randint(0, 1000), np.random.randint(0, 800)),
            "enemies_near": np.random.randint(0, 5),
            "in_combat": np.random.random() < 0.3,
            "safe_zone_near": np.random.random() < 0.2
        }
    
    def _capture_player_actions(self) -> List[Dict]:
        import keyboard
        import pyautogui
        
        actions = []
        keys = ['w', 'a', 's', 'd', 'space', 'shift', 'ctrl', 'e', 'q', 'r', 'f', 'tab', 'esc']
        for key in keys:
            if keyboard.is_pressed(key):
                actions.append({"type": "press", "key": key})
        
        mouse_x, mouse_y = pyautogui.position()
        if mouse_x != 0 or mouse_y != 0:
            actions.append({"type": "move", "x": mouse_x, "y": mouse_y})
        
        return actions
    
    def _calculate_reward(self, state: Dict) -> float:
        reward = 0
        if state.get("health", 0) > 50:
            reward += 1
        if state.get("enemies_near", 0) < 1:
            reward += 2
        if state.get("safe_zone_near", False):
            reward += 5
        return reward
    
    def _state_to_key(self, state: Dict) -> str:
        return f"{state.get('position', (0,0))}_{state.get('enemies_near', 0)}_{state.get('in_combat', False)}"
    
    def _best_action_for_state(self, state: Dict) -> Dict:
        state_key = self._state_to_key(state)
        if state_key in self.patterns and self.patterns[state_key]:
            actions = self.patterns[state_key]
            most_common = max(actions, key=actions.count)
            return most_common[0] if most_common else {"type": "idle"}
        return self._explore_action()
    
    def _explore_action(self) -> Dict:
        actions = [
            {"type": "press", "key": "w"},
            {"type": "press", "key": "a"},
            {"type": "press", "key": "s"},
            {"type": "press", "key": "d"},
            {"type": "press", "key": "space"},
            {"type": "press", "key": "shift"},
            {"type": "move", "x": np.random.randint(0, 1920), "y": np.random.randint(0, 1080)},
            {"type": "click", "x": np.random.randint(0, 1920), "y": np.random.randint(0, 1080)},
        ]
        return np.random.choice(actions)
    
    def _add_variation(self, actions: List[Dict]) -> List[Dict]:
        variations = []
        for action in actions:
            if action["type"] == "move":
                variations.append({
                    "type": "move",
                    "x": action["x"] + np.random.randint(-10, 10),
                    "y": action["y"] + np.random.randint(-10, 10)
                })
            else:
                variations.append(action)
        return variations
    
    def _analyze_patterns(self):
        for entry in self.action_history:
            state_key = self._state_to_key(entry["state"])
            actions = entry["actions"]
            self.patterns[state_key].extend(actions)
    
    def save_data(self):
        try:
            data = {
                "action_history": self.action_history[-1000:],
                "patterns": dict(self.patterns),
                "free_actions": self.free_actions[-500:],
                "total_actions": self.total_actions_recorded,
                "match_score": self.match_score,
                "free_score": self.free_score
            }
            with open("imitation_data.pkl", "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения: {e}")
    
    def load_data(self):
        try:
            with open("imitation_data.pkl", "rb") as f:
                data = pickle.load(f)
                self.action_history = data.get("action_history", [])
                self.patterns = defaultdict(list, data.get("patterns", {}))
                self.free_actions = data.get("free_actions", [])
                self.total_actions_recorded = data.get("total_actions", 0)
                self.match_score = data.get("match_score", 0.0)
                self.free_score = data.get("free_score", 0.0)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"⚠️ Ошибка загрузки: {e}")
    
    def get_status(self) -> Dict:
        mode = "idle"
        if self.is_recording:
            mode = "recording"
        elif self.is_playing:
            mode = "playing"
        elif self.is_cloning:
            mode = "cloning"
        elif self.is_free:
            mode = "free"
        
        return {
            "mode": mode,
            "actions_recorded": self.total_actions_recorded,
            "actions_played": self.total_actions_played,
            "free_actions": self.total_free_actions,
            "match_score": round(self.match_score, 2),
            "free_score": round(self.free_score, 2),
            "patterns": len(self.patterns)
        }