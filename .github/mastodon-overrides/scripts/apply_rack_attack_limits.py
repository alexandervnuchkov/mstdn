#!/usr/bin/env python3
"""
Точечно заменяет значения `limit:` в config/initializers/rack_attack.rb
исходного репозитория Mastodon на значения из YAML-файла с переопределениями.

Скрипт намеренно не использует внешние библиотеки (например, PyYAML),
чтобы не тянуть лишние зависимости на self-hosted раннере — формат
YAML-файла ограничен простыми парами `ключ: значение` без вложенности.

Использование:
    apply_rack_attack_limits.py <rack_attack.rb> <limits.yml>
"""

import re
import sys


def parse_simple_yaml(path):
    """Разбирает плоский YAML-файл вида `key: value` в словарь {str: int}."""
    limits = {}
    with open(path, "r", encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().strip("'\"")
            value = value.split("#", 1)[0].strip()
            if not value:
                continue
            limits[key] = int(value)
    return limits


# Ищет вызовы вида:
#   throttle('throttle_authenticated_api', limit: 300, period: 5.minutes)
# Имя правила и число limit: должны быть на одной строке — так оформлены
# все стандартные throttle-правила в rack_attack.rb Mastodon.
THROTTLE_RE = re.compile(
    r"(throttle\(\s*['\"])(?P<name>[^'\"]+)(['\"].*?limit:\s*)(?P<limit>\d+)"
)


def patch_file(rack_attack_path, limits):
    with open(rack_attack_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    changed = []

    def replace(match):
        name = match.group("name")
        if name in limits:
            new_limit = limits[name]
            old_limit = match.group("limit")
            if str(new_limit) != old_limit:
                changed.append((name, old_limit, new_limit))
            return f"{match.group(1)}{name}{match.group(3)}{new_limit}"
        return match.group(0)

    new_content = THROTTLE_RE.sub(replace, content)

    with open(rack_attack_path, "w", encoding="utf-8") as fh:
        fh.write(new_content)

    if changed:
        print("Изменены лимиты в rack_attack.rb:")
        for name, old, new in changed:
            print(f"  {name}: {old} -> {new}")
    else:
        print("Ни одно правило из limits.yml не найдено в rack_attack.rb "
              "(или значения уже совпадают) — файл не изменился.")

    unused = set(limits) - {name for name, *_ in changed}
    # unused может содержать и правила, чьи значения совпали с новыми —
    # это нормально, поэтому дополнительно не предупреждаем о них здесь.


def main():
    if len(sys.argv) != 3:
        print(f"Использование: {sys.argv[0]} <rack_attack.rb> <limits.yml>",
              file=sys.stderr)
        sys.exit(1)

    rack_attack_path, limits_path = sys.argv[1], sys.argv[2]
    limits = parse_simple_yaml(limits_path)
    patch_file(rack_attack_path, limits)


if __name__ == "__main__":
    main()
