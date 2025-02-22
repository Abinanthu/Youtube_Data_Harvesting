# Import necessary libraries for the application
import streamlit as st  # Streamlit for creating the user interface
import googleapiclient.discovery  # Google API client to interact with the YouTube API
import googleapiclient.errors  # Error handling for the YouTube API requests
import pyodbc  # For connecting to the SQL Server database
import sys  # For system-related operations
from streamlit_option_menu import option_menu  # For creating a navigation menu in Streamlit
import pandas as pd  # For data manipulation and analysis
import sqlite3  # For connecting to the SQLite database

# Define the YouTube API key (replace this with your actual API key)
api_key = "AIzaSyBMa5oA89m1rKpAcjVV844s61lyhEECmUA"

# Build the YouTube API client using the API key
# This allows us to make requests to the YouTube API to fetch data
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

# Function to establish a connection to the database
# This will allow us to insert data into the SQL Server database
def get_db_connection():
    try:
        # Connect to the database using the pyodbc library
        conn = pyodbc.connect(
            driver='{ODBC Driver 17 for SQL Server}',
            server='LENOVO-V130',
            database='YoutubeDataHarsvesting',
            trusted_connection='yes'
        )
        print("Connection created")  # Print a success message if the connection is successful
        return conn  # Return the connection object
    except pyodbc.Error as e:
        # Handle errors during the connection attempt
        print(f"Error connecting to the database: {e}")
        return None  # Return None if there was an error

# Function to fetch channel data from the YouTube API
def get_channel_data(channel_id):
    try:
        request = youtube.channels().list(part="snippet,contentDetails,statistics", id=channel_id)
        response = request.execute()
        
        if response['items']:
            data = {
                'channel_id': response['items'][0]['id'],
                'channel_name': response['items'][0]['snippet']['title'],
                'channel_des': response['items'][0]['snippet']['description'],
                'view_count': int(response['items'][0]['statistics']['viewCount']),
                'subscriber_count': int(response['items'][0]['statistics']['subscriberCount']),
                'video_count': int(response['items'][0]['statistics']['videoCount'])
            }
            return data
        else:
            return None
    except googleapiclient.errors.HttpError as e:
        print(f"Error fetching channel data: {e}")
        return None

# Function to fetch playlist data from the YouTube API
def get_playlist_data(channel_id):
    try:
        playlists_request = youtube.playlists().list(part="snippet,contentDetails", channelId=channel_id)
        playlists_response = playlists_request.execute()
        
        playlists = []
        if 'items' in playlists_response and playlists_response['items']:
            for playlist in playlists_response['items']:
                playlist_data = {
                    'playlist_id': playlist['id'],
                    'playlist_title': playlist['snippet']['title'],
                    'playlist_description': playlist['snippet']['description']
                }
                playlists.append(playlist_data)
        
        return playlists
    except googleapiclient.errors.HttpError as e:
        print(f"Error fetching playlist data: {e}")
        return None

# Function to fetch video data for a given channel
def get_video_data(channel_id):
    try:
        playlists_data = get_playlist_data(channel_id)
        video_data = []
        for playlist in playlists_data:
            playlist_id = playlist['playlist_id']
            videos_request = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=playlist_id)
            videos_response = videos_request.execute()

            for video in videos_response['items']:
                video_id = video['snippet']['resourceId']['videoId']
                video_title = video['snippet']['title']
                video_description = video['snippet']['description']

                video_data.append({
                    'video_id': video_id,
                    'video_title': video_title,
                    'video_description': video_description,
                    'playlist_id': playlist_id
                })

        return video_data
    except googleapiclient.errors.HttpError as e:
        print(f"Error fetching video data: {e}")
        return None

# Function to fetch comment data for videos
def get_comment_data(video_data):
    try:
        comment_data = []
        for video in video_data:
            video_id = video['video_id']
            comments_request = youtube.commentThreads().list(part="snippet,replies", videoId=video_id)
            comments_response = comments_request.execute()

            video_comments = []
            if 'items' in comments_response:
                for comment_item in comments_response['items']:
                    comment = comment_item['snippet']['topLevelComment']['snippet']['textDisplay']
                    video_comments.append(comment)

            for comment in video_comments:
                comment_data.append({
                    'video_id': video_id,
                    'comment_text': comment
                })

        return comment_data
    except googleapiclient.errors.HttpError as e:
        print(f"Error fetching comment data: {e}")
        return None

# Insert functions to save data into the SQL database
def insert_channel_data(conn, channel_data):
    try:
        cursor = conn.cursor()
        query = '''
            INSERT INTO channels (channel_id, channel_name, channel_description, view_count, subscriber_count, video_count)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (
            channel_data['channel_id'],
            channel_data['channel_name'],
            channel_data['channel_des'],
            channel_data['view_count'],
            channel_data['subscriber_count'],
            channel_data['video_count']
        ))
        conn.commit()
        print("Channel data inserted successfully.")
    except pyodbc.Error as e:
        print(f"Error inserting channel data: {e}")

def insert_playlist_data(conn, playlist_data, channel_id):
    try:
        cursor = conn.cursor()
        for playlist in playlist_data:
            query = '''
                INSERT INTO playlists (playlist_id, playlist_title, playlist_description, channel_id)
                VALUES (?, ?, ?, ?)
            '''
            cursor.execute(query, (
                playlist['playlist_id'],
                playlist['playlist_title'],
                playlist['playlist_description'],
                channel_id
            ))
        conn.commit()
        print(f"Inserted {len(playlist_data)} playlists successfully.")
    except pyodbc.Error as e:
        print(f"Error inserting playlist data: {e}")

def insert_video_data(conn, video_data, channel_id):
    try:
        cursor = conn.cursor()
        for video in video_data:
            query = '''
                INSERT INTO videos (video_id, video_title, video_description, channel_id)
                VALUES (?, ?, ?, ?)
            '''
            cursor.execute(query, (
                video['video_id'],
                video['video_title'],
                video['video_description'],
                channel_id
            ))
        conn.commit()
        print(f"Inserted {len(video_data)} videos successfully.")
    except pyodbc.Error as e:
        print(f"Error inserting video data: {e}")

def insert_comment_data(conn, comment_data, video_id):
    try:
        cursor = conn.cursor()
        for comment in comment_data:
            query = '''
                INSERT INTO comments (video_id, comment_text)
                VALUES (?, ?)
            '''
            cursor.execute(query, (
                video_id,
                comment['comment_text']
            ))
        conn.commit()
        print(f"Inserted {len(comment_data)} comments successfully.")
    except pyodbc.Error as e:
        print(f"Error inserting comment data: {e}")

# Streamlit UI setup for navigation and data fetching
menu_options = ["Channel Info", "Queries"]
selected = option_menu(None, menu_options, icons=['search', 'gear'], menu_icon="cast", default_index=0, orientation="horizontal")

# Adjust the title based on the selected page
if selected == "Channel Info":
    st.title("YouTube Channel Data Fetcher")
    st.write("Enter a YouTube Channel ID to get its data.")
# elif selected == "Queries":
#     st.title("YouTube Data Queries")
#     st.write("Select a query to retrieve data from the database.")

# Conditional Channel ID input (only visible on "Channel Info" page)
if selected == "Channel Info":
    channel_id_input = st.text_input("Enter Channel ID")

if selected == "Channel Info":
    if st.button('Fetch Channel Data'):
        if channel_id_input:
            channel_data = get_channel_data(channel_id_input)
            conn = get_db_connection()

            if channel_data:
                insert_channel_data(conn, channel_data)
                
                st.subheader("Channel Data")
                st.write(f"Channel Name: {channel_data['channel_name']}")
                st.write(f"Description: {channel_data['channel_des']}")
                st.write(f"View Count: {channel_data['view_count']}")
                st.write(f"Subscriber Count: {channel_data['subscriber_count']}")
                st.write(f"Video Count: {channel_data['video_count']}")

                playlist_data = get_playlist_data(channel_id_input)
                if playlist_data:
                    insert_playlist_data(conn, playlist_data, channel_id_input)
                    st.subheader("Playlists")
                    for playlist in playlist_data:
                        st.write(f"Playlist Title: {playlist['playlist_title']}")
                        st.write(f"Description: {playlist['playlist_description']}")
                else:
                    st.write("No playlists found.")
                
                video_data = get_video_data(channel_id_input)
                if video_data:
                    insert_video_data(conn, video_data, channel_id_input)
                    st.subheader("Videos")
                    for video in video_data:
                        st.write(f"Video Title: {video['video_title']}")
                        st.write(f"Description: {video['video_description']}")
                else:
                    st.write("No videos found.")

                comment_data = get_comment_data(video_data)
                if comment_data:
                    st.subheader("Comments")
                    for comment in comment_data:
                        st.write(f"Comment: {comment['comment_text']}")
                    insert_comment_data(conn, comment_data, video_data[0]['video_id'])
                else:
                    st.write("No comments found.")
            else:
                st.error("Channel not found or invalid channel ID.")
        else:
            st.error("Please enter a valid YouTube Channel ID.")

# import pyodbc
# import pandas as pd
# import streamlit as st

# Streamlit UI setup for navigation and data fetching
menu_options = ["Channel Info", "Queries"]
selected = st.selectbox("Select", menu_options)

# Function to connect to SQL Server
def get_db_connection():
    conn = pyodbc.connect(
        driver='{ODBC Driver 17 for SQL Server}',  # Driver for SQL Server
        server='LENOVO-V130',  # Your server name
        database='YoutubeDataHarsvesting',  # Your database name
        trusted_connection='yes'  # Trusted connection (Windows Authentication)
    )
    return conn

# Execute SQL query and return results as a DataFrame
def execute_query(query):
    conn = get_db_connection()  # Get a database connection
    try:
        result_df = pd.read_sql(query, conn)
        return result_df
    except Exception as e:
        st.error(f"Error executing query: {e}")
    finally:
        conn.close()  # Close the connection

# UI for Queries 
if selected == "Queries":
    st.title("YouTube Data Queries")

    # Define query options
    query_options = [
        "Video and Channel Info",
        "Channel with Most Videos",
        "Top 10 Most Viewed Videos",
        "Comments Count",
        "Total Views per Channel",
        "Channel with Videos Count"
    ]

    selected_query = st.selectbox("Select Query", query_options)

    # SQL Queries based on selected menu option
    if selected_query == "Video and Channel Info":
        query = """
            SELECT videos.video_title, channels.channel_name
            FROM videos
            JOIN channels ON videos.channel_id = channels.channel_id;
        """
        # Execute the query and fetch the result as a DataFrame
        result_df = execute_query(query)
        
        if result_df is not None:
            # Display the resulting DataFrame in Streamlit
            st.dataframe(result_df)

    elif selected_query == "Channel with Most Videos":
        query = """
            SELECT TOP 1 channels.channel_name, COUNT(videos.video_id) AS video_count
            FROM dbo.channels
            JOIN dbo.videos ON channels.channel_id = videos.channel_id
            GROUP BY channels.channel_name
            ORDER BY video_count DESC;

        """
        result_df = execute_query(query)
        if result_df is not None:
            st.dataframe(result_df)

    elif selected_query == "Top 10 Most Viewed Videos":
        query = """
                SELECT TOP 10 videos.video_title, channels.view_count
                FROM dbo.videos
                JOIN dbo.channels ON videos.channel_id = channels.channel_id
                ORDER BY channels.view_count DESC;
        """
        result_df = execute_query(query)
        if result_df is not None:
            st.dataframe(result_df)

    elif selected_query == "Comments Count":
        query = """
            SELECT video_title, COUNT(comments.comment_id) AS comment_count
            FROM dbo.videos
            JOIN dbo.comments ON videos.video_id = comments.video_id
            GROUP BY video_title;
        """
        result_df = execute_query(query)
        if result_df is not None:
            st.dataframe(result_df)

    # elif selected_query == "Videos with Most Likes":
    #     query = """
    #         SELECT video_title, likes
    #         FROM dbo.videos
    #         ORDER BY likes DESC
    #         LIMIT 10;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)

    # elif selected_query == "Likes and Dislikes per Video":
    #     query = """
    #         SELECT video_title, likes, dislikes
    #         FROM dbo.videos;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)

    elif selected_query == "Total Views per Channel":
        query = """
                SELECT channel_name, SUM(view_count) AS total_views
                FROM dbo.channels
                GROUP BY channel_name;

        """
        result_df = execute_query(query)
        if result_df is not None:
            st.dataframe(result_df)

    # elif selected_query == "Channels in 2022":
    #     query = """
    #         SELECT channel_name, created_date
    #         FROM dbo.channels
    #         WHERE YEAR(created_date) = 2022;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)

    # elif selected_query == "Average Video Duration":
    #     query = """
    #         SELECT AVG(duration) AS avg_duration
    #         FROM dbo.videos;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)

    # elif selected_query == "Videos with Most Comments":
    #     query = """
    #         SELECT video_title, COUNT(comments.comment_id) AS comment_count
    #         FROM dbo.videos
    #         JOIN dbo.comments ON videos.video_id = comments.video_id
    #         GROUP BY video_title
    #         ORDER BY comment_count DESC
    #         LIMIT 10;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)



    elif selected_query == "Channel with Videos Count":
        query = """
            select channel_name,video_count from channels;
        """
        result_df = execute_query(query)
        if result_df is not None:
            st.dataframe(result_df)

    # elif selected_query == "Top 10 Most Viewed Videos":
    #     query = """
    #         SELECT video.video_title, channel.channel_name, video.view_count
    #         FROM video
    #         JOIN channel ON video.channel_id = channel.channel_id
    #         ORDER BY video.view_count DESC
    #         LIMIT 10;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)

    elif selected_query == "Comments Count":
        query = """
            SELECT video.video_title, COUNT(comment.comment_id) AS comment_count
            FROM video
            JOIN comment ON video.video_id = comment.video_id
            GROUP BY video.video_title;
        """
        result_df = execute_query(query)
        if result_df is not None:
            st.dataframe(result_df)

    # elif selected_query == "Videos with Most Likes":
    #     query = """
    #         SELECT video.video_title, channel.channel_name, video.like_count
    #         FROM video
    #         JOIN channel ON video.channel_id = channel.channel_id
    #         ORDER BY video.like_count DESC
    #         LIMIT 1;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)

    # elif selected_query == "Likes and Dislikes per Video":
    #     query = """
    #         SELECT video.video_title, SUM(video.like_count) AS total_likes, SUM(video.dislike_count) AS total_dislikes
    #         FROM video
    #         GROUP BY video.video_title;
    #     """
    #     result_df = execute_query(query)
    #     if result_df is not None:
    #         st.dataframe(result_df)
