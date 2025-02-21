YouTube Data Fetcher and Analysis with Streamlit
This repository contains a Streamlit application designed to fetch, store, and analyze YouTube channel data. The app uses the YouTube API to gather information about channels, playlists, videos, and comments, and stores this data in a SQL Server database. It provides a user-friendly interface for viewing the data and running SQL queries for analysis.

Key Features
Fetch Data: Fetch YouTube channel details, playlists, videos, and comments using the YouTube API.
Database Integration: Store the fetched data in an SQL Server database for easy retrieval and analysis.
Streamlit Interface: Use the intuitive Streamlit interface for seamless navigation between fetching data and running queries.
SQL Query Analysis: Run pre-defined SQL queries to analyze YouTube data, such as:
Top 10 most viewed videos
Video and channel information
Channel with the most videos
Total views per channel
Comments count on videos
Technologies Used
Python: The primary language for developing the app.
Streamlit: A framework for creating interactive, web-based applications.
Google API Client: For interacting with the YouTube API.
pyodbc: For connecting to SQL Server and handling database interactions.
SQL Server: Used for storing and querying YouTube data.
Requirements
Before running the app, ensure you have the following installed:

Python 3.x (preferably the latest version)
Streamlit: Install via pip install streamlit
Google API Client: Install via pip install google-api-python-client
pyodbc: Install via pip install pyodbc
SQL Server: Ensure you have a running SQL Server instance.
Setup Instructions
Clone the repository:

bash
Copy
git clone https://github.com/yourusername/YouTube-Data-Fetcher.git
cd YouTube-Data-Fetcher
Install the required libraries: Run the following command to install all necessary dependencies:

bash
Copy
pip install -r requirements.txt
Set up SQL Server:

Set up a database in SQL Server (you can use the provided YoutubeDataHarvesting as a sample).
Ensure the database has the required tables for channels, playlists, videos, and comments.
Set up your YouTube API key:

Replace the placeholder api_key variable in the script with your own YouTube API key.
python
Copy
api_key = "YOUR_YOUTUBE_API_KEY"
Run the Streamlit app: After setting up, run the app with the following command:

bash
Copy
streamlit run app.py
Interact with the App:

Enter a YouTube Channel ID and press the Fetch Channel Data button to retrieve data about the channel, playlists, videos, and comments.
Navigate to the Queries section to run various SQL queries and view the results.
How to Use
Channel Info:

Enter a valid YouTube Channel ID and click Fetch Channel Data to retrieve channel details like name, description, view count, subscriber count, and video count.
Fetch playlists, videos, and comments associated with the channel.
SQL Queries:

In the Queries section, select a query option to analyze data in the database. Available options include:
Video and Channel Information
Channel with Most Videos
Top 10 Most Viewed Videos
Comments Count per Video
Total Views per Channel
Channel with Video Count
Data Analysis:

View the results of SQL queries as tables directly in the Streamlit interface.
Sample SQL Queries
Here are some sample SQL queries that you can execute from the app:

Video and Channel Info
sql
Copy
SELECT videos.video_title, channels.channel_name
FROM videos
JOIN channels ON videos.channel_id = channels.channel_id;
Channel with Most Videos
sql
Copy
SELECT TOP 1 channels.channel_name, COUNT(videos.video_id) AS video_count
FROM dbo.channels
JOIN dbo.videos ON channels.channel_id = videos.channel_id
GROUP BY channels.channel_name
ORDER BY video_count DESC;
Top 10 Most Viewed Videos
sql
Copy
SELECT TOP 10 videos.video_title, channels.view_count
FROM dbo.videos
JOIN dbo.channels ON videos.channel_id = channels.channel_id
ORDER BY channels.view_count DESC;
Comments Count
sql
Copy
SELECT video_title, COUNT(comments.comment_id) AS comment_count
FROM dbo.videos
JOIN dbo.comments ON videos.video_id = comments.video_id
GROUP BY video_title;
Total Views per Channel
sql
Copy
SELECT channel_name, SUM(view_count) AS total_views
FROM dbo.channels
GROUP BY channel_name;
Contribution
Feel free to fork the repository and make improvements! If you encounter any issues or have suggestions for new features, please open an issue or submit a pull request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
