import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import os
from datetime import datetime, timedelta
import requests
import re
from tkcalendar import DateEntry
import time
import asyncio
import aiohttp
import logging

class TwitterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Twitter Data Fetcher")
        self.master.geometry("600x600")
        self.tweets_fetched = 2977  # Initialize with the current count
        self.tweets_fetched_file = "tweets_fetched.json"
        self.setup_logging()
        self.load_tweets_fetched()
        self.create_widgets()
        self.load_keys()

    def setup_logging(self):
        logging.basicConfig(filename='twitter_app.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('TwitterApp')

    def create_widgets(self):
        key_frame = ttk.LabelFrame(self.master, text="Twitter API Keys")
        key_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(key_frame, text="Bearer Token:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.bearer_token_entry = ttk.Entry(key_frame, width=50, show="*")
        self.bearer_token_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(key_frame, text="Save Keys", command=self.save_keys).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        user_frame = ttk.LabelFrame(self.master, text="Twitter Users")
        user_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(user_frame, text="CSV File:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.csv_entry = ttk.Entry(user_frame, width=40)
        self.csv_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(user_frame, text="Browse", command=self.browse_csv).grid(row=0, column=2, padx=5, pady=5)

        date_frame = ttk.LabelFrame(self.master, text="Date Range")
        date_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(date_frame, text="Start Date:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.start_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_frame, text="End Date:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.end_date = DateEntry(date_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.end_date.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.master, text="Fetch Tweets", command=self.fetch_tweets).pack(pady=10)

        self.status_label = ttk.Label(self.master, text="")
        self.status_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=5)

        self.tweets_fetched_label = ttk.Label(self.master, text=f"Tweets fetched this month: {self.tweets_fetched}")
        self.tweets_fetched_label.pack(pady=5)

        ttk.Button(self.master, text="Reset Tweets Fetched", command=self.reset_tweets_fetched).pack(pady=5)

    def load_keys(self):
        if os.path.exists('twitter_keys.json'):
            with open('twitter_keys.json', 'r') as f:
                keys = json.load(f)
                self.bearer_token_entry.insert(0, keys.get('bearer_token', ''))

    def save_keys(self):
        keys = {'bearer_token': self.bearer_token_entry.get()}
        with open('twitter_keys.json', 'w') as f:
            json.dump(keys, f)
        messagebox.showinfo("Success", "Keys saved successfully!")

    def browse_csv(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if filename:
            self.csv_entry.delete(0, tk.END)
            self.csv_entry.insert(0, filename)

    def load_tweets_fetched(self):
        if os.path.exists(self.tweets_fetched_file):
            with open(self.tweets_fetched_file, 'r') as f:
                data = json.load(f)
                self.tweets_fetched = data.get('tweets_fetched', 2977)
        else:
            self.tweets_fetched = 2977
        self.update_tweets_fetched_label()

    def save_tweets_fetched(self):
        with open(self.tweets_fetched_file, 'w') as f:
            json.dump({'tweets_fetched': self.tweets_fetched}, f)

    def update_tweets_fetched(self, count):
        self.tweets_fetched += count
        self.save_tweets_fetched()
        self.update_tweets_fetched_label()

    def update_tweets_fetched_label(self):
        if hasattr(self, 'tweets_fetched_label'):
            self.tweets_fetched_label.config(text=f"Tweets fetched this month: {self.tweets_fetched}")

    def reset_tweets_fetched(self):
        self.tweets_fetched = 0
        self.save_tweets_fetched()
        self.update_tweets_fetched_label()
        messagebox.showinfo("Success", "Tweets fetched count reset to 0.")

    def bearer_oauth(self, r):
        r.headers["Authorization"] = f"Bearer {self.bearer_token_entry.get()}"
        r.headers["User-Agent"] = "v2UserTweetsPython"
        return r

    async def get_user_id_async(self, session, username):
        url = f"https://api.twitter.com/2/users/by/username/{username}"
        self.logger.info(f"Fetching user ID for username: {username}")
        async with session.get(url, headers=self.bearer_oauth(requests.Request()).headers) as response:
            if response.status != 200:
                self.logger.error(f"Error fetching user ID for {username}: {response.status}")
                raise Exception(f"Request returned an error: {response.status} {await response.text()}")
            data = await response.json()
            user_id = data['data']['id']
            self.logger.info(f"User ID for {username}: {user_id}")
            return user_id

    async def get_user_tweets_async(self, session, user_id, start_time, end_time, max_tweets=1000):
        url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {
            "max_results": 100,
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tweet.fields": "created_at,text",
            "expansions": "author_id",
            "user.fields": "id,name,username"
        }

        tweets = []
        next_token = None
        request_count = 0
        retry_count = 0
        max_retries = 5

        while len(tweets) < max_tweets and request_count < 15 and retry_count < max_retries:
            if next_token:
                params['pagination_token'] = next_token

            self.logger.info(f"Making request for user {user_id}. Request count: {request_count}")
            async with session.get(url, headers=self.bearer_oauth(requests.Request()).headers, params=params) as response:
                request_count += 1
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    sleep_time = min(retry_after * (2 ** retry_count), 900)  # Max sleep of 15 minutes
                    self.logger.warning(f"Rate limit exceeded. Sleeping for {sleep_time} seconds.")
                    await asyncio.sleep(sleep_time)
                    retry_count += 1
                    continue

                if response.status != 200:
                    self.logger.error(f"Request returned an error: {response.status} {await response.text()}")
                    raise Exception(f"Request returned an error: {response.status} {await response.text()}")

                response_json = await response.json()
                self.logger.info(f"Received response for user {user_id}. Tweets in response: {len(response_json.get('data', []))}")
                
                if 'data' in response_json:
                    new_tweets = response_json['data']
                    tweets.extend(new_tweets)
                    self.update_tweets_fetched(len(new_tweets))
                    if 'next_token' in response_json.get('meta', {}):
                        next_token = response_json['meta']['next_token']
                        self.logger.info(f"Pagination token received: {next_token}")
                    else:
                        self.logger.info("No more pagination tokens. All tweets fetched.")
                        break
                else:
                    self.logger.info("No tweets in response. Breaking loop.")
                    break

            if self.tweets_fetched >= 10000:  # Monthly limit
                self.logger.warning("Monthly tweet limit reached. Stopping.")
                break

            await asyncio.sleep(1)  # Small delay between requests

        self.logger.info(f"Finished fetching tweets for user {user_id}. Total tweets: {len(tweets)}")
        return tweets[:max_tweets]

    async def fetch_user_tweets_async(self, session, username, start_time, end_time):
        try:
            if not re.match(r'^[a-zA-Z0-9_]{1,15}$', username):
                raise ValueError(f"Invalid username format: {username}")

            user_id = await self.get_user_id_async(session, username)
            tweets_data = await self.get_user_tweets_async(session, user_id, start_time, end_time)

            output_dir = "twitter_data"
            os.makedirs(output_dir, exist_ok=True)

            if tweets_data:
                with open(os.path.join(output_dir, f"{username}_tweets.txt"), 'w', encoding='utf-8') as f:
                    for tweet in tweets_data:
                        f.write(f"{tweet['created_at']}: {tweet['text']}\n\n")
                self.logger.info(f"Tweets for {username} saved successfully. Count: {len(tweets_data)}")
                return f"Tweets for {username} saved successfully! Count: {len(tweets_data)}"
            else:
                self.logger.info(f"No tweets found for {username} in the specified date range.")
                return f"No tweets found for {username} in the specified date range."
        except ValueError as ve:
            self.logger.error(f"ValueError for {username}: {str(ve)}")
            return str(ve)
        except Exception as e:
            self.logger.error(f"Error fetching tweets for {username}: {str(e)}")
            return f"Failed to fetch tweets for {username}: {str(e)}"

    async def fetch_all_users_tweets(self, usernames, start_date, end_date):
        async with aiohttp.ClientSession() as session:
            results = []
            for username in usernames:
                self.logger.info(f"Fetching tweets for user: {username}")
                result = await self.fetch_user_tweets_async(session, username, start_date, end_date)
                results.append(result)
                await asyncio.sleep(5)  # Add a 5-second delay between users
            return results

    def fetch_tweets(self):
        if not self.bearer_token_entry.get():
            messagebox.showerror("Error", "Please enter the Bearer Token.")
            return

        if not self.csv_entry.get():
            messagebox.showerror("Error", "Please select a CSV file with Twitter usernames.")
            return

        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()

        if start_date > end_date:
            messagebox.showerror("Error", "Start date must be before end date.")
            return

        usernames = []
        with open(self.csv_entry.get(), 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            usernames = [row[0].strip() for row in reader if row]

        start_time = datetime.combine(start_date, datetime.min.time())
        end_time = datetime.combine(end_date, datetime.max.time())

        self.logger.info(f"Starting to fetch tweets for {len(usernames)} users")
        self.status_label.config(text="Fetching tweets...")
        self.progress_bar['value'] = 0
        self.master.update()

        results = asyncio.run(self.fetch_all_users_tweets(usernames, start_time, end_time))

        for index, result in enumerate(results, 1):
            self.status_label.config(text=result)
            self.progress_bar['value'] = (index / len(usernames)) * 100
            self.master.update()

        self.logger.info(f"Finished fetching tweets. Total fetched this month: {self.tweets_fetched}")
        self.status_label.config(text=f"Finished fetching tweets. Total fetched this month: {self.tweets_fetched}")
        self.progress_bar['value'] = 100

if __name__ == "__main__":
    root = tk.Tk()
    app = TwitterApp(root)
    root.mainloop()