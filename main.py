import json
from dataclasses import dataclass

from pycaw.pycaw import (
    AudioSession,
    AudioUtilities,
    ISimpleAudioVolume,
    IAudioMeterInformation,
)


@dataclass
class TheMutenatorConfig:
    meeting_app: str
    volume_downcrase: int
    exceptions: list[str]


def read_config() -> TheMutenatorConfig:
    with open('the_mutenator.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    config = TheMutenatorConfig(
        volume_downcrase=data.get('volume_downcrase', 20),
        exceptions=data.get('exceptions', []),
        meeting_app=data.get('meeting_app', 'teams')
    )

    config.exceptions.append(config.meeting_app)

    return config


def full_app_name(app: str) -> str:
    if app.endswith('.exe'):
        return app.lower()
    else:
        return f'{app.lower()}.exe'


def meeting_in_progress(config: TheMutenatorConfig) -> bool:
    sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
    for session in sessions:
        session: AudioSession

        if session.Process and session.Process.name().lower() == full_app_name(config.meeting_app):
            audio_meter = session._ctl.QueryInterface(IAudioMeterInformation)
            audio_level = audio_meter.GetPeakValue()
            if audio_level > 0:
                return True
    return False


def change_apps_volume(config: TheMutenatorConfig, volume_change: int) -> None:
    exceptions: list[str] = [
        full_app_name(app)
        for app in config.exceptions
    ]

    sessions: list[AudioSession] = AudioUtilities.GetAllSessions()
    for session in sessions:
        session: AudioSession

        if not session.Process or session.Process.name().lower() in exceptions:
            continue

        app_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        
        volume_atual = app_volume.GetMasterVolume()
        novo_volume = volume_atual + volume_change / 100

        novo_volume = min(0, novo_volume)
        novo_volume = max(1, novo_volume)

        app_volume.SetMasterVolume(novo_volume, None)

        print(f'Volume do app {session.Process.name().lower()} alterado de {volume_atual:02f} para {novo_volume:02f}')


def mute_apps() -> None:
    config: TheMutenatorConfig = read_config()
    active_meeting: bool = False

    while True:
        if meeting_in_progress(config):
            if not active_meeting:
                change_apps_volume(config, config.volume_downcrase * -1)
                active_meeting = True
        elif active_meeting:
            change_apps_volume(config, config.volume_downcrase)
            active_meeting = False


if __name__ == '__main__':
    mute_apps()
