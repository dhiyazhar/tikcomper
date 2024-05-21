import re
import os
import requests
import math

from json import dumps
from argparse import ArgumentParser
from comment.Comment import Comment  # Adjusted import statement
import logging  # Logging should be imported separately

if __name__ == '__main__':
    argp: ArgumentParser = ArgumentParser()
    argp.add_argument("--url", '-u', type=str, default='7170139292767882522')
    argp.add_argument("--size", '-s', type=int, default=50)
    argp.add_argument("--output", '-o', type=str, default='data')
    args = argp.parse_args()

    if "vm.tiktok.com" in args.url or "vt.tiktok.com" in args.url:
        videoid = requests.head(args.url, stream=True, allow_redirects=True, timeout=5).url.split("/")[5].split("?", 1)[0]
    elif re.match("^\d+$", args.url):
        videoid = args.url
    else:
        videoid = args.url.split("/")[5].split("?", 1)[0]
    
    comment: Comment = Comment()

    json_full, dummy = [], {}

    for i in range(math.ceil(args.size / 50)):
        data: dict = comment.execute(videoid, i * 50)

        if not os.path.exists(args.output):
            os.makedirs(args.output)

        if data:
            dummy = data
            json_full += data['comments']

            with open(f'{args.output}/{videoid}_{i * 50}-{(i + 1) * 50}.json', 'w') as file:
                file.write(dumps(data, ensure_ascii=False, indent=2))
                logging.info(f'Output data : {args.output}/{videoid}_{i * 50}-{(i + 1) * 50}.json')

    comment.to_csv(args.output, videoid)