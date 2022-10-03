### Program with to get penguinz0 Youtube data
### @ IQ

#====================================================================================================================#
# Preliminaries
#====================================================================================================================#
#-------------------------------------------------------------------------------------------------------------------#
# Libraries
#-------------------------------------------------------------------------------------------------------------------#

#Basic libraries
import pandas as pd
import numpy as np
from dateutil import parser
import isodate

#Paths
import os
from pathlib import Path
from sys import api_version

# Google API
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build

# Data visualization libraries
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
sns.set(style="darkgrid", color_codes=True)

# NLP libraries
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('punkt')
from wordcloud import WordCloud

#====================================================================================================================#
# My Path
#====================================================================================================================#

__file__ = 'test.py'
codefile_directory=Path(__file__).absolute().parent
print(codefile_directory)
code_folder=str(codefile_directory)+"\\"
print(code_folder)

#====================================================================================================================#
# Funtions
#====================================================================================================================#

os.chdir(code_folder)

from mainfunctions import get_channel_stats
from mainfunctions import get_video_ids
from mainfunctions import get_video_details
from mainfunctions import get_comments_in_videos

#====================================================================================================================#
# Parameters
#====================================================================================================================#

api_key = 'AIzaSyDt29H6_4ZRFulkdEbeb-FC5tO3Hoh3zHQ'
api_service_name="youtube"
api_version="v3"

#Get credentials and create an API client
youtube = build('youtube', 'v3', developerKey=api_key)

channel_ids = ['UCtYLUTtgS3k1Fg4y5tAhLbw', # Statquest
               'UCCezIgC97PvUuR4_gbFUs5g', # Corey Schafer
               'UCfzlCWGWYyIQ0aLC5w48gBQ', # Sentdex
               'UCNU_lfiiWBdtULKOw6X0Dig', # Krish Naik
               'UCzL_0nIe8B4-7ShhVPfJkgw', # DatascienceDoJo
               'UCLLw7jmFsvfIVaUFsLs8mlQ', # Luke Barousse 
               'UCiT9RITQ9PW6BhXK0y2jaeg', # Ken Jee
               'UC7cs8q-gJRlGwj4A8OmCmXg', # Alex the analyst
               'UC2UXDak6o7rBm23k3Vv5dww', # Tina Huang
              ]

playlist_id = ['PLRD7N-Zrj2DOt_DFJg7IaJJCaLpsLJEwz']
video_ids = ['']

#====================================================================================================================#
# Test
#====================================================================================================================#

channel_data = get_channel_stats(youtube, channel_ids)
channel_data

# Convert count columns to numeric columns
numeric_cols = ['subscribers', 'views', 'totalVideos']
channel_data[numeric_cols] = channel_data[numeric_cols].apply(pd.to_numeric, errors='coerce')

#Let's take a look at the number of subscribers per channel to have a view of how popular the channels are when compared 
# with one another.
sns.set(rc={'figure.figsize':(10,8)})
ax = sns.barplot(x='channelName', y='subscribers', data=channel_data.sort_values('subscribers', ascending=False))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/1000) + 'K'))
plot = ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)

#Next, we will look at the rank considering the total number of views of the channels. The rank is fairly similar to the 
# subscriber count rank. Sentdex and Corey Schafer remain the two most popular channels considering both subscribers and 
# views. Interestingly, some channels have more subscribers but less views and vice versa. For example, Ken Jee channel 
# has significantly more subscribers than Luke Barousse channel, but slightly less views in total.

ax = sns.barplot(x='channelName', y='views', data=channel_data.sort_values('views', ascending=False))
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x/1000) + 'K'))
plot = ax.set_xticklabels(ax.get_xticklabels(),rotation = 90)

#--------------------------------------------------------------------------------------------------------------------#
# Get video statistics for all the channels

# Create a dataframe with video statistics and comments from all channels

video_df = pd.DataFrame()
comments_df = pd.DataFrame()

for c in channel_data['channelName'].unique():
    print("Getting video information from channel: " + c)
    playlist_id = channel_data.loc[channel_data['channelName']== c, 'playlistId'].iloc[0]
    video_ids = get_video_ids(youtube, playlist_id)
    
    # get video data
    video_data = get_video_details(youtube, video_ids)
    # get comment data
    comments_data = get_comments_in_videos(youtube, video_ids)

    # append video data together and comment data toghether
    video_df = video_df.append(video_data, ignore_index=True)
    comments_df = comments_df.append(comments_data, ignore_index=True)


video_df
comments_df

# Write video data to CSV file for future references
video_df.to_csv('video_data_top10_channels.csv')
comments_df.to_csv('comments_data_top10_channels.csv')

#--------------------------------------------------------------------------------------------------------------------#
# Preprocessing & Feature engineering

#Check for empty values
video_df.isnull().any()

video_df.publishedAt.sort_values().value_counts()

cols = ['viewCount', 'likeCount', 'favoriteCount', 'commentCount']
video_df[cols] = video_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)

#Enriching data
# Create publish day (in the week) column
video_df['publishedAt'] =  video_df['publishedAt'].apply(lambda x: parser.parse(x)) 
video_df['pushblishDayName'] = video_df['publishedAt'].apply(lambda x: x.strftime("%A")) 

# convert duration to seconds
video_df['durationSecs'] = video_df['duration'].apply(lambda x: isodate.parse_duration(x))
video_df['durationSecs'] = video_df['durationSecs'].astype('timedelta64[s]')

# Add number of tags
video_df['tagsCount'] = video_df['tags'].apply(lambda x: 0 if x is None else len(x))

# Comments and likes per 1000 view ratio
video_df['likeRatio'] = video_df['likeCount']/ video_df['viewCount'] * 1000
video_df['commentRatio'] = video_df['commentCount']/ video_df['viewCount'] * 1000

# Title character length
video_df['titleLength'] = video_df['title'].apply(lambda x: len(x))

video_df.head()

#--------------------------------------------------------------------------------------------------------------------#
#Exploratory analysis

plt.rcParams['figure.figsize'] = (18, 6)
sns.violinplot(video_df['channelTitle'], video_df['viewCount'], palette = 'pastel')
plt.title('Views per channel', fontsize = 14)
plt.show()

#Does the number of likes and comments matter for a video to get more views?
fig, ax =plt.subplots(1,2)
sns.scatterplot(data = video_df, x = "commentCount", y = "viewCount", ax=ax[0])
sns.scatterplot(data = video_df, x = "likeCount", y = "viewCount", ax=ax[1])

fig, ax =plt.subplots(1,2)
sns.scatterplot(data = video_df, x = "commentRatio", y = "viewCount", ax=ax[0])
sns.scatterplot(data = video_df, x = "likeRatio", y = "viewCount", ax=ax[1])

#Does the video duration matter for views and interaction (likes/ comments)?
sns.histplot(data=video_df[video_df['durationSecs'] < 10000], x="durationSecs", bins=30)

fig, ax =plt.subplots(1,2)
sns.scatterplot(data = video_df, x = "durationSecs", y = "commentCount", ax=ax[0])
sns.scatterplot(data = video_df, x = "durationSecs", y = "likeCount", ax=ax[1])

#Does title length matter for views?
sns.scatterplot(data = video_df, x = "titleLength", y = "viewCount")

#Wordcloud for words in title
stop_words = set(stopwords.words('english'))
video_df['title_no_stopwords'] = video_df['title'].apply(lambda x: [item for item in str(x).split() if item not in stop_words])

all_words = list([a for b in video_df['title_no_stopwords'].tolist() for a in b])
all_words_str = ' '.join(all_words)

def plot_cloud(wordcloud):
    plt.figure(figsize=(30, 20))
    plt.imshow(wordcloud) 
    plt.axis("off");

wordcloud = WordCloud(width = 2000, height = 1000, random_state=1, background_color='black', 
                      colormap='viridis', collocations=False).generate(all_words_str)
plot_cloud(wordcloud)

#Number of tags vs views
sns.scatterplot(data = video_df, x = "tagsCount", y = "viewCount")

#Which day in the week are most videos uploaded?
day_df = pd.DataFrame(video_df['pushblishDayName'].value_counts())
weekdays = [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_df = day_df.reindex(weekdays)
ax = day_df.reset_index().plot.bar(x='index', y='pushblishDayName', rot=0)

#Wordcloud for video comments
stop_words = set(stopwords.words('english'))
comments_df['comments_no_stopwords'] = comments_df['comments'].apply(lambda x: [item for item in str(x).split() if item not in stop_words])

all_words = list([a for b in comments_df['comments_no_stopwords'].tolist() for a in b])
all_words_str = ' '.join(all_words)

wordcloud = WordCloud(width = 2000, height = 1000, random_state=1, background_color='black', 
                      colormap='viridis', collocations=False).generate(all_words_str)
plot_cloud(wordcloud)





channel_ids = ['UC4EQHfzIbkL_Skit_iKt1aA']
playlist_id = ['PLRD7N-Zrj2DOt_DFJg7IaJJCaLpsLJEwz']
video_ids = ['']


if __name__ == "__main__":
    get_video_ids(youtube, playlist_id)
    get_video_details(youtube, video_ids)
    get_comments_in_videos(youtube, video_ids)