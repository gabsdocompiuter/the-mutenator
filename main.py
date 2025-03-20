import json
import psutil
import time
from dataclasses import dataclass


@dataclass
class TheMutenatorConfig:
    meeting_app: str
    volume_downcrase: int
    processes: list[str]


def read_config() -> TheMutenatorConfig:
    with open('the_mutenator.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    config = TheMutenatorConfig(
        volume_downcrase=data.get('volume_downcrase', 20),
        processes=data.get('processes', []),
        meeting_app=data.get('meeting_app', 'teams')
    )

    return config


def meeting_in_progress(config: TheMutenatorConfig) -> bool:
    for process in psutil.process_iter(['name']):
        if process.info['name'] == config.meeting_app:
            try:
                if process.net_connections(kind='inet'):
                    return True
            except:
                pass
    return False


def mute_apps() -> None:
    config: TheMutenatorConfig = read_config()

    while True:
        print(f'Reunião em progesso: {meeting_in_progress(config)}')
        time.sleep(3)


if __name__ == '__main__':
    mute_apps()
