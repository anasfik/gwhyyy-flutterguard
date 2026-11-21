#!/usr/bin/env python3
"""Check the real nginx counter: URL and container name are required arguments."""
import datetime
import json
import subprocess
import sys
import urllib.parse
import urllib.request
import uuid


def main():
    base, container = sys.argv[1:]
    marker = "privacy-check-" + uuid.uuid4().hex
    since = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for path in ("/cli/", "/" + marker):
        query = urllib.parse.urlencode({"p": path, "extra": marker})
        request = urllib.request.Request(
            base.rstrip("/") + "/_c/play?" + query,
            data=b"",
            headers={"User-Agent": marker, "Referer": "https://example.org/" + marker},
        )
        with urllib.request.urlopen(request, timeout=15) as response:
            assert response.status == 204, response.status
    logs = subprocess.run(
        ["docker", "logs", "--since", since, container],
        check=True, capture_output=True, text=True, timeout=15,
    )
    output = logs.stdout + logs.stderr
    assert marker not in output, "Counter leaked a raw path, query, user agent or referrer"
    events = [json.loads(line) for line in output.splitlines()
              if line.startswith('{"event":"play_cta_clicked"')]
    assert {"/cli/", "other"} <= {event["page"] for event in events}, events
    assert all(set(event) == {"event", "time", "page"} for event in events), events
    print("PASS real POST counter logs only event, time and bounded page bucket")


if __name__ == "__main__":
    main()
