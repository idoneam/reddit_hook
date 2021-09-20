# reddit listener webhook

sends the newest posts from some subreddit to some webhook

### requirements

this program requires the following environment variables to be set to function:

+ `IRH_SUBREDDIT_NAME`: name of the subreddit the hook will listen to (ex: `all`, `pics`, `askreddit`)
+ `IRH_TARGET_WEBHOOK_URL`: url of the webhook to which new posts should be sent to
+ `IRH_LOG_WEBHOOK_URL`: url of the webhook to which errors will be logged
+ `IRH_SLEEP_DURATION`: duration for which the bot should sleep, in seconds, needs to parsable to a float

### docker

docker can be used to deploy this webhook by running the following commands (remember to substitute empty placeholders with real values)

```sh
docker build . -t irh:latest
docker run \
	-e IRH_SUBREDDIT_NAME='' \
	-e IRH_TARGET_WEBHOOK_URL='' \
	-e IRH_LOG_WEBHOOK_URL='' \
	-e IRH_SLEEP_DURATION='' \
	-d irh:latest
```

we also provide prebuilt docker images synced to the latest commit of the main branch, which can be used as follows (again, remember to substitute empty placeholders with real values)

```sh
docker pull ghcr.io/idoneam/reddit_hook:main
docker run \
    -e IRH_SUBREDDIT_NAME='' \
    -e IRH_TARGET_WEBHOOK_URL='' \
    -e IRH_LOG_WEBHOOK_URL='' \
    -e IRH_SLEEP_DURATION='' \
    -d ghcr.io/idoneam/reddit_hook:main
```
