import random
import time
import os
import operator
import requests
from datetime import datetime


def main(subr: str, trg_hook: str, log_hook: str, sleep_dur: float):
    try:
        min_time = datetime.utcnow()
        while True:
            permalinks = []
            for data in map(
                operator.itemgetter("data"),
                requests.get(
                    f"https://www.reddit.com/r/{subr}/new.json",
                    headers={
                        "User-Agent": "".join(
                            chr(random.randint(32, 126)) for _ in range(16)
                        )
                    },
                ).json()["data"]["children"],
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
                    json={"content": f"https://old.reddit.com{permalink}"},
                )
            if permalinks:
                min_time = permalinks[0][1]
            time.sleep(sleep_dur)
    except:
        import traceback

        requests.post(
            log_hook,
            json={
                "content": "LOG: r/{} webhook has crashed\nerror log:```\n{}```".format(
                    subr, traceback.format_exc().replace("```", "\\`\\`\\`")
                ),
                "username": f"r/{subr} webhook log",
            },
        )


if __name__ == "__main__":
    main(
        os.environ["IRH_SUBREDDIT_NAME"],
        os.environ["IRH_TARGET_WEBHOOK_URL"],
        os.environ["IRH_LOG_WEBHOOK_URL"],
        float(os.environ["IRH_SLEEP_DURATION"]),
    )
