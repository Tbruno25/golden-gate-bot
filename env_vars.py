import json
import os


# Get Reddit keys
reddit_credentials_json = os.getenv("REDDIT_APPLICATION_JSON")
reddit_credentials = json.loads(reddit_credentials_json, strict=False)

# Get Google keys
google_credentials_json = os.getenv("GOOGLE_APPLICATION_JSON")
google_credentials = json.loads(google_credentials_json, strict=False)
with open("google-key.json", "w") as file:
    json.dump(google_credentials, file)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-key.json"

# Get Database keys
database_host = os.getenv("QOVERY_REDIS_ZBBCDA9B9_HOST")
database_port = os.getenv("QOVERY_REDIS_ZBBCDA9B9_PORT")
database_password = os.getenv("QOVERY_REDIS_ZBBCDA9B9_PASSWORD")