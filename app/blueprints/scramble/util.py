from sqlalchemy import create_engine
from config import config, S3_KEY, S3_SECRET, S3_BUCKET, S3_OBJECT_LOCATION
import os, re, boto3, botocore

database_uri = config['default'].SQLALCHEMY_DATABASE_URI
engine = create_engine(database_uri)
db = engine.connect()

s3 = boto3.client(
    "s3",
    aws_access_key_id = S3_KEY,
    aws_secret_access_key = S3_SECRET
)

def get_categories():
    """Get all available game categories from SQL enum"""
    
    # query = f"SELECT COLUMN_TYPE AS game_category_names FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='dig_ital' AND TABLE_NAME='scramble_games' AND COLUMN_NAME='game_category'"
    # allcatquery = str(db.execute(query).fetchone()[0])
    # allcat = []
    # cat = ""
    # for i in range(6, len(allcatquery)):
    #     if allcatquery[i] in ',)':
    #         allcat.append(cat)
    #         cat = ""
    #     elif allcatquery[i]=="'":
    #         continue
    #     else:
    #         cat += allcatquery[i]
    # return allcatquery, allcat

    query = f"SELECT DISTINCT game_category from scramble_games"
    allcatquery = db.execute(query).fetchall()
    
    uniquecats = ()

    if len(allcatquery) > 0:
        uniquecats = allcatquery[0]

    allcat = ['Abbigliamento','Albergo','Banca','Bar/Ristorante','Casa','Chiaroveggente','Concerto','Dottore','Meccanico','Mercato','Mezzi di comunicazione','Mezzi di trasporto','Scuola','Tempo']

    for cat in uniquecats:
        if cat not in allcat:
            allcat.append(cat)

    return allcat

# Upload media files for video & audio scramble games to Amazon S3
# Code from https://www.zabana.me/notes/flask-tutorial-upload-files-amazon-s3

def upload_file_to_s3(f, media_file_name):

    try:
        s3.upload_fileobj(
            f,
            S3_BUCKET,
            media_file_name,
            ExtraArgs = {
                "ACL": "public-read",
                "ContentType": f.content_type
            }
        )
    except Exception as e:
        return e


def copy_to_s3_permanent_folder(game_title):

    copy_source = {
        'Bucket': S3_BUCKET,
        'Key': f'temporary/{game_title}'
    }

    s3.copy(
        copy_source,
        S3_BUCKET,
        f'uploaded_games/{game_title}',
            ExtraArgs = {
                "ACL": "public-read",
            }
        )


def delete_from_s3(s3_folder, game_title):

    s3.delete_object(Bucket=S3_BUCKET, Key=f'{s3_folder}/{game_title}')


def get_s3_object_path(media_file_name):
    return f'{S3_OBJECT_LOCATION}/{media_file_name}'

