# YouTube Data Harvesting Tool

This Streamlit application allows you to fetch and store YouTube channel data, including channel details, playlists, videos, and comments, into a SQL Server database. It also provides a query interface to retrieve and display data from the database.

## Table of Contents

-   [Features](#features)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Installation](#installation)
    -   [Configuration](#configuration)
-   [Usage](#usage)
    -   [Channel Info Page](#channel-info-page)
    -   [Queries Page](#queries-page)
-   [Database Schema](#database-schema)
-   [Queries Available](#queries-available)
-   [Contributing](#contributing)
-   [License](#license)

## Features

-   Fetch and store YouTube channel details, playlists, videos, and comments.
-   Store fetched data in a SQL Server database.
-   Query the database to retrieve and display data.
-   User-friendly Streamlit interface.

## Getting Started

### Prerequisites

-   Python 3.6+
-   SQL Server
-   YouTube Data API v3 key

### Installation

1.  Clone the repository:

    ```bash
    git clone [repository_url]
    cd [repository_directory]
    ```

2.  Install the required libraries:

    ```bash
    pip install streamlit google-api-python-client pyodbc pandas streamlit-option-menu
    ```

### Configuration

1.  **YouTube API Key:**
    -   Obtain a YouTube Data API v3 key from the [Google Cloud Console](https://console.cloud.google.com/).
    -   Replace `"YOUR_API_KEY"` in the script with your actual API key.

2.  **SQL Server Database:**
    -   Create a database named `YoutubeDataHarsvesting`.
    -   Create the tables as described in the [Database Schema](#database-schema) section.
    -   Modify the `get_db_connection` function in the script to match your SQL Server connection details.

## Usage

1.  Run the Streamlit application:

    ```bash
    streamlit run your_script_name.py
    ```

### Channel Info Page

-   Enter a YouTube Channel ID and click "Fetch Channel Data."
-   The application will fetch and display channel details, playlists, videos, and comments, and store them in the database.

### Queries Page

-   Select a query from the dropdown menu.
-   The application will execute the query and display the results in a table.

## Database Schema

```sql
CREATE TABLE channels (
    channel_id VARCHAR(255) PRIMARY KEY,
    channel_name VARCHAR(255),
    channel_description TEXT,
    view_count INT,
    subscriber_count INT,
    video_count INT
);

CREATE TABLE playlists (
    playlist_id VARCHAR(255) PRIMARY KEY,
    playlist_title VARCHAR(255),
    playlist_description TEXT,
    channel_id VARCHAR(255),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

CREATE TABLE videos (
    video_id VARCHAR(255) PRIMARY KEY,
    video_title VARCHAR(255),
    video_description TEXT,
    channel_id VARCHAR(255),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
);

CREATE TABLE comments (
    comment_id INT PRIMARY KEY IDENTITY(1,1),
    video_id VARCHAR(255),
    comment_text TEXT,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);
