import argparse
import json
import pandas as pd

from apiclient.discovery import build
from csv import writer
from urllib.parse import urlparse, parse_qs

#Functions to get the key and build API service
def get_keys(filename):
    with open(filename) as f:
        key = f.readline()
    DEVELOPER_KEY = key
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return {'key': key, 'name': 'youtube', 'version': 'v3'}

def build_service(filename):
    with open(filename) as f:
        key = f.readline()

    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 developerKey=key)

#Function to get YouTube video ID based v parametr in the video URL
def get_id(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]

#Function to get the comments
def get_comments(**kwargs):
    """
    ty: 
    https://python.gotrained.com/youtube-api-extracting-comments/#Cache_Credentials
    https://www.pingshiuanchua.com/blog/post/using-youtube-api-to-analyse-youtube-comments-on-python
    """

    #List declaration to return desired contents
    comments, commentsId, repliesCount, likesCount, updatedAt, viewerRating, videoId = [], [], [], [], [], [], []

    #Clean kwargs

    #Parameters required for query
    kwargs['part'] = kwargs.get('part', 'snippet').split()
    kwargs['maxResults'] = kwargs.get('maxResults', 100)
    kwargs['textFormat'] = kwargs.get('textFormat', 'plainText')
    kwargs['order'] = kwargs.get('order', 'time')
    service = kwargs.pop('service')

    #Parametrs required for dealing with output file and token file containing the data on where the extraction has stopped
    write_lbl = kwargs.pop('write_lbl', True)
    csv_filename = kwargs.pop('csv_filename')
    token_filename = kwargs.pop('token_filename')


    #Get the first page of comments
    response = service.commentThreads().list(
        **kwargs
    ).execute()

    #Continue until we crash or reach the end
    page = 0
    while response:
        print(f'page {page}')
        page += 1
        index = 0
        for item in response['items']:
            print(f"comment {index}")
            index += 1

            #Pull the data from the JSON response
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_id = item['snippet']['topLevelComment']['id']
            reply_count = item['snippet']['totalReplyCount']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']
            updated_at = item['snippet']['topLevelComment']['snippet']['updatedAt']
            viewer_rating = item['snippet']['topLevelComment']['snippet']['viewerRating']
            video_id = item['snippet']['videoId']

            #Place the data in the declared list (see above)
            comments.append(comment)
            commentsId.append(comment_id)
            repliesCount.append(reply_count)
            likesCount.append(like_count)
            updatedAt.append(updated_at)
            viewerRating.append(viewer_rating)
            videoId.append(video_id)

            if write_lbl:
                with open(f'{csv_filename}.csv', 'a+') as f:
                    # https://thispointer.com/python-how-to-append-a-new-row-to-an-existing-csv-file/#:~:text=Open%20our%20csv%20file%20in,in%20the%20associated%20csv%20file
                    csv_writer = writer(f)
                    csv_writer.writerow([comment, comment_id, reply_count, like_count, viewer_rating, updated_at, video_id])

        #Check if there's a next page
        if 'nextPageToken' in response:
            with open(f'{token_filename}.txt', 'a+') as f:
                f.write(kwargs.get('pageToken', ''))
                f.write('\n')
            kwargs['pageToken'] = response['nextPageToken']
            response = service.commentThreads().list(
                **kwargs
            ).execute()
        else:
            break

    return {
        'Comments': comments,
        'Comment ID' : commentsId,
        'Reply Count' : repliesCount,
        'Like Count' : likesCount,
        'Updated At' : updatedAt,
        'Viewer Rating': viewerRating,
        'Video ID': videoId,
    }

#Function to save output in .csv file
def save_to_csv(output_dict, video_id, output_filename):
    output_df = pd.DataFrame(output_dict, columns = output_dict.keys())
    output_df.to_csv(f'{output_filename}.csv')

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--part', help='Desired properties of commentThread', default='snippet')
    parser.add_argument('--maxResults', help='Max results per page', default=100)
    parser.add_argument('--write_lbl', help="Update csv after each comment?", default=True)
    parser.add_argument('--csv_filename', default=None)
    parser.add_argument('--token_filename', default=None)
    parser.add_argument('--video_url', default='https://www.youtube.com/watch?v=gZjQROMAh_s')
    parser.add_argument('--order', default='time')
    parser.add_argument('--apikey', default='../apikey.json')
    parser.add_argument('--pageToken', default=None)
    args = parser.parse_args()

    # build kwargs from args
    kwargs = vars(args)

    service = build_service(kwargs.pop('apikey'))
    video_id = get_id(kwargs.pop('video_url'))

    if not args.csv_filename:
        args.csv_filename = video_id + "_csv"

    if not args.token_filename:
        args.token_filename = video_id + "_page_token"

    if not kwargs.get('pageToken'):
        kwargs.pop('pageToken')

    kwargs['videoId'] = video_id
    kwargs['service'] = service
    output_dict = get_comments(**kwargs)

    args.csv_filename += "_final"
    save_to_csv(output_dict, video_id, args.csv_filename)
    
if __name__ == '__main__':
    #Eecute the above functions
    main()
