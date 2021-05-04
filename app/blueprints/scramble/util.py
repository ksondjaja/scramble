from sqlalchemy import create_engine
from config import config
import os, re

database_uri = config['default'].SQLALCHEMY_DATABASE_URI
engine = create_engine(database_uri)
db = engine.connect()

def getCategories():
    """Get all available game categories from SQL enum"""
    
    query = f"SELECT COLUMN_TYPE AS game_category_names FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dig_ital' AND TABLE_NAME='scramble_games' AND COLUMN_NAME='game_category'"
    allcatquery = str(db.execute(query).fetchone()[0])
    allcat = []
    cat = ""
    for i in range(6, len(allcatquery)):
        if allcatquery[i] in ',)':
            allcat.append(cat)
            cat = ""
        elif allcatquery[i]=="'":
            continue
        else:
            cat += allcatquery[i]
    return allcatquery, allcat

# def getVideoId(youtubelink):
#     """Get just the video ID from a YouTube video link"""

#     if 'watch?v=' in youtubelink:
#         ind = youtubelink.index('watch?v=')
#         ind += 8
#         if len(youtubelink)<(ind+11):
#             return 'invalid'
#         else:
#             videoid = youtubelink[ind:(ind+11)]
#             return videoid
#     else:
#         return 'invalid'
