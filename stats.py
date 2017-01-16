import click
try:
    from config import *
except ImportError:
    click.echo("Copy config-sample.py to config.py and edit with your tumblr api key")
    exit()
import pytumblr
from datetime import (
    datetime,
    timedelta,
)

def get_client():
    client = pytumblr.TumblrRestClient(tumblr_api_key)
    return client
    
@click.command()
@click.argument('blog')
@click.option('--days', default=2)
def posts_by_date(blog, days):
    client = get_client()

    days_ago = datetime.now() - timedelta(days=days)
    click.echo("Requesting {} days posts, back to {}".format(
        days, days_ago.strftime('%x %X')))
    enough = False
    offset = 0
    posts = []
    while not enough:
        click.echo("Requesting posts starting with post {}".format(offset))
        post_info = client.posts('{}.tumblr.com'.format(blog), offset=offset)
        posts.extend(post_info['posts'])
        last_post_time = datetime.fromtimestamp(posts[-1]['timestamp'])
        if last_post_time < days_ago:
            enough = True
        else:
            click.echo("Last post time {}. Getting more".format(last_post_time.strftime('%x %X')))
            offset = offset + 20

    post_date_data = {}
    post_hour_data = {}
    bad_hour_posts = {}

    for post in posts:
        post_time = datetime.fromtimestamp(post['timestamp'])
        post_day = post_time.strftime('%x')
        post_hour = post_time.hour
        post_weekday = post_time.weekday()

        if post_day in post_date_data:
            post_date_data[post_day] = post_date_data[post_day] + 1
        else:
            post_date_data[post_day] = 1

        if post_hour in post_hour_data:
            post_hour_data[post_hour] = post_hour_data[post_hour] + 1
        else:
            post_hour_data[post_hour] = 1

        mon = 0
        tue = 1
        wed = 2
        thu = 3
        fri = 4
        sat = 5
        sun = 6
        if ((post_weekday not in [fri, sat] and post_hour >= 23) or
            (post_weekday not in [sat, sun] and post_hour < 7)):
            bad_hour_posts[post['timestamp']] = "{:>20}".format(
                post_time.strftime("%c"))

            
    print("Posts by date:")
    sorted_dates = sorted(post_date_data.keys())
    for day in sorted_dates:
        print("{:>10}: {}".format(day, post_date_data[day]))

    print("\nPosts by hour:")
    sorted_hours = sorted(post_hour_data.keys())
    for hour in sorted_hours:
        print("  {:02d}:00: {}".format(hour, post_hour_data[hour]))

    print("\nPosts at bad times: {} total".format(len(bad_hour_posts)))
    sorted_posts = sorted(bad_hour_posts.keys())
    for timestamp in sorted_posts:
        print("  {}".format(bad_hour_posts[timestamp]))
                           

if __name__ == '__main__':
    posts_by_date()
