from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import os

extract = URLExtract()

def filter_by_user(selected_user, df):
    if selected_user != 'Overall':
        return df[df['user'] == selected_user]
    return df

def read_stop_words(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    else:
        print(f"Warning: Stop words file {file_path} not found.")
        return ""

def fetch_stats(selected_user, df):
    df = filter_by_user(selected_user, df)
    
    # Number of messages
    num_messages = df.shape[0]
    
    # Total number of words
    words = [word for message in df['message'] for word in message.split()]
    
    # Number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    
    # Number of links shared
    links = [link for message in df['message'] for link in extract.find_urls(message)]
    
    return num_messages, len(words), num_media_messages, len(links)

def most_busy_users(df):
    user_counts = df['user'].value_counts().head()
    user_percentage = (df['user'].value_counts() / df.shape[0] * 100).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return user_counts, user_percentage

def create_wordcloud(selected_user, df):
    stop_words = read_stop_words('stop_hinglish.txt')
    
    df = filter_by_user(selected_user, df)
    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]
    
    def remove_stop_words(message):
        return " ".join([word for word in message.lower().split() if word not in stop_words])
    
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    
    return df_wc

def most_common_words(selected_user, df):
    stop_words = read_stop_words('stop_hinglish.txt')
    
    df = filter_by_user(selected_user, df)
    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]
    
    words = [word for message in temp['message'] for word in message.lower().split() if word not in stop_words]
    
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

import matplotlib.pyplot as plt

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Extracting emojis from the messages
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    # Counting the occurrences of each emoji
    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    # Plotting the pie chart
    if not emoji_df.empty:
        plt.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows (adjust this based on your OS)
        
        fig, ax = plt.subplots()
        ax.pie(emoji_df[1].head(), labels=[f"{emj} {cnt}" for emj, cnt in zip(emoji_df[0].head(), emoji_df[1].head())], autopct="%0.2f%%")
        plt.title("Top Emojis Used")
        plt.show()

    return emoji_df


def monthly_timeline(selected_user, df):
    df = filter_by_user(selected_user, df)
    
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    
    timeline['time'] = timeline.apply(lambda row: f"{row['month']}-{row['year']}", axis=1)
    
    return timeline

def daily_timeline(selected_user, df):
    df = filter_by_user(selected_user, df)
    
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    
    return daily_timeline

def week_activity_map(selected_user, df):
    df = filter_by_user(selected_user, df)
    
    return df['day_name'].value_counts()

def month_activity_map(selected_user, df):
    df = filter_by_user(selected_user, df)
    
    return df['month'].value_counts()

def activity_heatmap(selected_user, df):
    df = filter_by_user(selected_user, df)
    
    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    
    return user_heatmap
