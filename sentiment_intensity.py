from datetime import datetime
from tkinter import Frame

import nltk
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn as sns
# sns.set(style='darkgrid', context='talk', palette='Dark2')
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from nltk.corpus import stopwords

from gather_data import ForumDataSource

nltk.download('stopwords')
nltk.download('vader_lexicon')
stop_words = stopwords.words("english")
import gzip

# Shortest allowed comment (ignore comments shorter than X chars)
MINIMUM_COMMENT_LENGTH=20

# set up sentiment analyzer
sia = SIA()

"""
Input: df (load from file)
Apply SIA Polarity Score to dataframe
Return dataframe with results
"""
def apply_sentiment_intensity(df: pd.DataFrame):
    """
    :param df: Dataframe containing text to analyze
    :return: DataFrame indexed by date
    """
    # Map the (dict) results of SIA polarity scores onto our data
    x = pd.json_normalize(df.text.apply(sia.polarity_scores))

    # Add date column, index by date
    reduced_df: pd.DataFrame = df[['date']].join(x)
    reduced_df.set_index('date', inplace=True)

    return reduced_df


"""
Input: Reddit dataframe from the ForumDataSource
"""
def plot_sentiment_intensity(df):

    # Apply moving-window average, and plot results
    df.ewm(span=100).mean().plot(
        label='Moving average',
        cmap=plt.cm.rainbow)


"""
This is a convenience method - you don't have to use it, but it's one way to display a pyplot chart inside the GUI.

Makes a pyplot inside a Frame

Input: 
DataFrame containing sentiment intensity scores (from apply_sentiment_intensity).

Output: A tkinter Frame containing the plot
"""
def plot_sentiment_intensity_in_frame(df, master, sub_name):
    # the figure that will contain the plot
    fig = Figure(figsize=(5, 5),
                 dpi=100)

    # adding the subplot
    ax = fig.add_subplot(111)
    canvas_frame = Frame(master)
    # creating the Tkinter canvas
    # containing the Matplotlib figure
    canvas = FigureCanvasTkAgg(fig,
                               master=canvas_frame)
    canvas.draw()

    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()

    # Apply moving-window average, and plot results
    df.ewm(span=100).mean().plot(
        label='Moving average',
        cmap=plt.cm.rainbow,
        ax=ax)

    print('Plotted moving average')

    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas,
                                   canvas_frame)
    toolbar.update()
    toolbar.pack_configure(expand=True)

    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()

    return canvas_frame

import glob

if __name__ == '__main__':
    # Monero subreddit comment data
    filename = 'data/reddit/Monero_comments_1598932800_1596254400.json.gz'

    data_source = ForumDataSource()
    df = data_source.load_from_file(filename)

    df = apply_sentiment_intensity(df)
    plot_sentiment_intensity(df)