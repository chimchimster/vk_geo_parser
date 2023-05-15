import os
import asyncio
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()
x = os.environ.get('VK_TOKEN')
print(x)



parser = argparse.ArgumentParser(description='Hello, World!')
parser.add_argument('-p', '--print_args', help='Prints arguments ma fa ka', default='Simple string', nargs='*')
args = parser.parse_args()
print(args.print_args)

async def get_resp(url):
    return requests.get(url).text


async def main():
    task = asyncio.create_task(get_resp('https://google.com'))
    done, pending = await asyncio.wait({task})

    if task in done:
        print('WORK IS DONE!')

asyncio.run(main())

print(os.environ['HOME'])
