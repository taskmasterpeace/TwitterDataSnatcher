### Twitter Data Snatcher

🎉 Welcome to the **Twitter Data Snatcher**! This application allows you to fetch tweets from multiple Twitter users within a specified date range, using the Twitter API. It's designed to make it easy to collect and save tweets for analysis or archiving purposes. 

## Features

- 🔑 **Securely Save API Keys**: Save and load your Twitter API bearer token securely.
- 📄 **CSV Input**: Load a CSV file with Twitter handles to fetch tweets from.
- 📅 **Date Range Selection**: Specify the start and end dates for fetching tweets.
- 🚀 **Fetch Tweets**: Retrieve tweets from the specified users within the given date range.
- 📊 **Progress Tracking**: Track the progress of tweet fetching.
- 🗃️ **Save Fetched Tweets**: Save fetched tweets to text files for each user.
- 🔄 **Reset Tweet Count**: Reset the count of tweets fetched for the month.

## Usage

### Prerequisites

1. **Python**: Ensure you have Python installed.
2. **Dependencies**: Install required packages using:
    ```sh
    pip install -r requirements.txt
    ```

### Setup

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/twitter-data-fetcher.git
    cd twitter-data-fetcher
    ```

2. **Run the Application**:
    ```sh
    python twitter_app.py
    ```

### User Guide

1. **API Keys**:
   - Enter your Twitter API Bearer Token in the "Bearer Token" field.
   - Click "Save Keys" to securely save your API key.

2. **Load Twitter Users**:
   - Prepare a CSV file with Twitter handles (without the `@` symbol). The format should be:
     ```csv
     twitter_handle
     user1
     user2
     user3
     ```
   - Click "Browse" to select your CSV file.

3. **Select Date Range**:
   - Choose the start and end dates using the date picker.

4. **Fetch Tweets**:
   - Click "Fetch Tweets" to start fetching tweets.
   - Monitor the progress and status messages.

5. **Reset Tweets Fetched**:
   - Click "Reset Tweets Fetched" to reset the monthly tweet count.

### Example Use Case

#### Scenario

You are a social media analyst who needs to collect tweets from various influencers over the past month to analyze trends and sentiment.

#### Steps

1. **Prepare CSV File**:
   - Create a CSV file `influencers.csv` with the following content:
     ```csv
     twitter_handle
     influencer1
     influencer2
     influencer3
     ```

2. **Run the Application**:
   - Launch the Twitter Data Fetcher and load your `influencers.csv`.

3. **Select Date Range**:
   - Set the start date to the beginning of the month and the end date to the current date.

4. **Fetch Tweets**:
   - Click "Fetch Tweets" and let the application collect the tweets.
   - Once completed, you will have text files with tweets for each influencer in the `twitter_data` directory.

5. **Analyze Data**:
   - Use the saved tweets for your sentiment analysis and trend identification.

## Contributions

Feel free to contribute to the project by submitting issues or pull requests.

## License

This project is licensed under the MIT License.

---

Enjoy fetching tweets! 🐦✨

---

**Note**: Ensure to add the required dependencies in `requirements.txt`:
```txt
tkinter
requests
tkcalendar
aiohttp
logging
```
