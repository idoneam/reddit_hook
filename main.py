import operator
import os
import random
import time
import traceback
from datetime import datetime
import requests


def main(subr: str, trg_hook: str, log_hook: str, sleep_dur: float):
    requests.post(
        log_hook,
        json={
            "content": f"r/{subr} webhook started",
            "username": f"r/{subr} webhook log",
        },
    )
    min_time = datetime.utcnow()
    while True:
        try:
            permalinks = []
            req = requests.get(
                f"https://www.reddit.com/r/{subr}/new.json",
                headers={
                    "User-Agent": fr"{chr(random.randint(33,126))}{''.join(chr(random.randint(32, 126)) for _ in range(15))}"
                },
            )
            assert (
                req.status_code == 200
            ), f"request to {req.url} returned {req.status_code}"
            for data in map(
                operator.itemgetter("data"), req.json()["data"]["children"]
            ):
                post_time = datetime.utcfromtimestamp(data["created_utc"])
                if post_time <= min_time:
                    break
                permalinks.append((data["permalink"], post_time))
            else:
                requests.post(
                    log_hook,
                    json={
                        "content": f"LOG: more than 25 posts were made in the last {sleep_dur} seconds on r/{subr}",
                        "username": f"r/{subr} webhook log",
                    },
                )
            for permalink in map(operator.itemgetter(0), reversed(permalinks)):
                requests.post(
                    trg_hook,
                    json={"content": f"https://www.reddit.com{permalink}"},
                )
            if permalinks:
                min_time = permalinks[0][1]
        except Exception:
            requests.post(
                log_hook,
                json={
                    "content": "```\n{}```".format(
                        traceback.format_exc().replace("```", "\\`\\`\\`")
                    ),
                    "username": f"r/{subr} webhook log",
                },
            )
        finally:
            time.sleep(sleep_dur)


if __name__ == "__main__":
    main(
        os.environ["IRH_SUBREDDIT_NAME"],
        os.environ["IRH_TARGET_WEBHOOK_URL"],
        os.environ["IRH_LOG_WEBHOOK_URL"],
        float(os.environ["IRH_SLEEP_DURATION"]),
    )
