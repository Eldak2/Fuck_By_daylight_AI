from src.music_controller import MusicController

class MediaHandler:
    def __init__(self, agent):
        self.agent = agent

    def handle(self, user_goal: str, use_voice: bool) -> str:
        goal_lower = user_goal.lower()
        voice = self.agent.voice

        if "музыка" in goal_lower or "плей" in goal_lower or "песня" in goal_lower:
            if "плей" in goal_lower or "play" in goal_lower or "включи" in goal_lower:
                result = MusicController.play_pause()
            elif "стоп" in goal_lower or "выключи" in goal_lower:
                result = MusicController.play_pause()
            elif "след" in goal_lower or "next" in goal_lower:
                result = MusicController.next_track()
            elif "пред" in goal_lower or "prev" in goal_lower:
                result = MusicController.prev_track()
            else:
                result = MusicController.play_pause()
            if use_voice and voice:
                voice.speak(result)
            return result

        if "громкость" in goal_lower or "звук" in goal_lower:
            if "+" in goal_lower or "увеличь" in goal_lower:
                result = MusicController.volume_up()
            elif "-" in goal_lower or "уменьш" in goal_lower:
                result = MusicController.volume_down()
            elif "выкл" in goal_lower or "mute" in goal_lower:
                result = MusicController.mute()
            else:
                result = MusicController.volume_up()
            if use_voice and voice:
                voice.speak(result)
            return result

        return None