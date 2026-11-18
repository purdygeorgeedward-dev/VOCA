"""VOCA fork: some CI matrices are `${{ fromJSON(<upstream> && '<all>' || '<fork>') }}`.

Upstream VoiceStudio gets every leg; the fork drops macOS runners,
which never start (Apple Silicon) or often time out (Intel) there. Tests check the upstream legs, so this returns them.
"""
import json
import re

_UPSTREAM = re.compile(r"^\$\{\{ fromJSON\(github\.repository == 'debpalash/VoiceStudio' && '(.*?)' \|\| '(.*?)'\) \}\}$")


def upstream(value):
    if isinstance(value, str):
        match = _UPSTREAM.match(value)
        assert match, f"unexpected matrix expression: {value}"
        return json.loads(match.group(1))
    return value


def fork(value):
    if isinstance(value, str):
        return json.loads(_UPSTREAM.match(value).group(2))
    return value
