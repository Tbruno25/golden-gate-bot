from datetime import datetime
from google.cloud import vision
from num2words import num2words
from praw import Reddit
from redis import StrictRedis
import json
import os


subreddit = "sanfrancisco"

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


class Bot:
    def __init__(self, subreddit_target):

        # Reddit stuff
        self.reddit = Reddit(
            client_id=reddit_credentials["client_id"],
            client_secret=reddit_credentials["client_secret"],
            username=reddit_credentials["username"],
            password=reddit_credentials["password"],
            user_agent=reddit_credentials["user_agent"],
        )
        self.subreddit = self.reddit.subreddit(subreddit_target)

        # Google Vision stuff
        self.vision_client = vision.ImageAnnotatorClient()
        self.vision_image = vision.Image()
        self.api_limit = 1_000

        # Database stuff
        self.database = StrictRedis(
            host=database_host, port=database_port, password=database_password, db=0
        )
        self.empty_dict = {"detected": 0, "analyzed": []}

        # Bot stuff
        self.analyzed = None
        self.detected = None
        self.id = None
        self.key = None
        self.url = None

    def get_date_created(self) -> str:
        """Return current month and year"""
        epoch = self.post.created
        date = datetime.fromtimestamp(epoch)
        return f"{date.month}-{date.year}"

    def parse_reddit_post(self, post):
        self.post = post
        self.key = self.get_date_created()
        self.id = self.post.id
        self.url = self.post.url

    def check_if_new_post(self):
        if self.id not in self.analyzed:
            self.analyzed.append(self.id)
            return True
        return False

    def load_database(self):
        if self.database.exists(self.key):
            db = json.loads(self.database.get(self.key))
        else:
            db = self.empty_dict
        self.analyzed = db["analyzed"]
        self.detected = db["detected"]

    def save_database(self):
        db = {"analyzed": self.analyzed, "detected": self.detected}
        self.database.set(self.key, json.dumps(db))

    def detect_image_in_post(self):
        """Return true if reddit post ends with common image extension"""
        image_extensions = (".gif", ".jpg", ".jpeg", ".png")
        detected = self.url.endswith(image_extensions)
        return detected

    def detect_golden_gate(self):
        """Return true if golden gate is detected within image"""
        if len(self.analyzed) >= self.api_limit:
            raise Exception("Google Vision API limit reached for this month.")
        self.vision_image.source.image_uri = self.url
        response = self.vision_client.landmark_detection(image=self.vision_image)
        for landmark in response.landmark_annotations:
            if "Golden Gate" in str(landmark):
                self.detected += 1
                return True
        return False

    def reply_to_post(self):
        times = num2words(self.detected, ordinal=True)
        self.post.reply(
            f"""Photo of Golden Gate Bridge Detected!\n
                This is the {times} time this month :)"""
        )

    def run(self):
        for post in self.subreddit.new():
            self.parse_reddit_post(post)
            if self.detect_image_in_post():
                self.load_database()
                if self.check_if_new_post():
                    if self.detect_golden_gate():
                        self.reply_to_post()
                    self.save_database()


if __name__ == "__main__":
    reddit_bot = Bot(subreddit_target=subreddit)
    reddit_bot.run()
