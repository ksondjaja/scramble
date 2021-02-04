from sqlalchemy import create_engine
import os, re

engine = create_engine('mysql://root:kontravoid@localhost/project_italia')
db = engine.connect()

def getCategories(table):
    """Get all available game categories from SQL enum"""
    
    query = f"SELECT COLUMN_TYPE AS game_category_names FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='project_italia' AND TABLE_NAME='{table}' AND COLUMN_NAME='game_category'"
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

def getVideoId(youtubelink):
    """Get just the video ID from a YouTube video link"""

    if 'watch?v=' in youtubelink:
        ind = youtubelink.index('watch?v=')
        ind += 8
        if len(youtubelink)<(ind+11):
            return 'invalid'
        else:
            videoid = youtubelink[ind:(ind+11)]
            return videoid
    else:
        return 'invalid'
