import operator
import os
import random
import time
import traceback

import requests


class Non200Error(Exception):
    def __init__(self, code: int, *args):
        super().__init__(*args)
        self.code: int = code


def main(
    subr: str,
    trg_hook: str,
    log_hook: str,
    sleep_dur: float,
    req_size: int,
    get_timeout: float | None,
    post_timeout: float | None,
):
    def get_data(after: str = "", limit: int = req_size):
        req: requests.Response = requests.get(
            f"https://www.reddit.com/r/{subr}/new.json?limit={limit}&after={after}",
            headers={
                "User-Agent": rf"{chr(random.randint(33,126))}{''.join(chr(random.randint(32, 126)) for _ in range(15))}"
            },
            timeout=get_timeout,
        )
        if req.status_code != 200:
            raise Non200Error(
                req.status_code, f"request to {req.url} returned {req.status_code}"
            )

        return map(operator.itemgetter("data"), req.json()["data"]["children"])

    def get_posts(last_post: str) -> list[dict]:
        data = get_data()
        posts: list[dict] = []
        while True:
            for item in data:
                if item["name"] == last_post:
                    break
                posts.append(item)
            else:
                data = get_data(posts[-1]["name"])
                continue
            return posts

    def post_links(posts: list[dict]):
        for permalink in map(operator.itemgetter("permalink"), reversed(posts)):
            requests.post(
                trg_hook,
                json={"content": f"https://www.reddit.com{permalink}"},
                timeout=post_timeout,
            )
        return posts[0]["name"]

    def log(curr_exc: Exception, prev_exc: Exception | None):
        if not (
            isinstance(curr_exc, Non200Error)
            and isinstance(prev_exc, Non200Error)
            and curr_exc.code == prev_exc.code
        ):
            requests.post(
                log_hook,
                json={
                    "content": "```\n{}```".format(
                        "\n".join(traceback.format_exception(curr_exc)).replace(
                            "```", "\\`\\`\\`"
                        )
                    ),
                    "username": f"r/{subr} webhook log",
                },
                timeout=post_timeout,
            )
        return curr_exc

    requests.post(
        log_hook,
        json={
            "content": f"r/{subr} webhook started",
            "username": f"r/{subr} webhook log",
        },
        timeout=post_timeout,
    )

    # limit set to 3 because anything less returns no results at all
    last_post: str = next(get_data(limit=3))["name"]
    last_exc: Exception | None = None

    while True:
        try:
            posts: list[dict] = get_posts(last_post)
            if posts:
                last_post = post_links(posts)
        except Exception as exc:
            last_exc = log(exc, last_exc)
        else:
            last_exc = None
        finally:
            time.sleep(sleep_dur)


if __name__ == "__main__":
    main(
        os.environ["IRH_SUBREDDIT_NAME"],
        os.environ["IRH_TARGET_WEBHOOK_URL"],
        os.environ["IRH_LOG_WEBHOOK_URL"],
        float(os.environ["IRH_SLEEP_DURATION"]),
        int(os.environ.get("IRH_REQUEST_SIZE", 25)),
        float(os.environ["IRH_GET_TIMEOUT"])
        if "IRH_GET_TIMEOUT" in os.environ
        else None,
        float(os.environ["IRH_POST_TIMEOUT"])
        if "IRH_POST_TIMEOUT" in os.environ
        else None,
    )
