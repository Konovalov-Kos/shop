import os, requests
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from prod_site.celery import app
from pathlib import Path

def get_way(url, data):
    if data == 'prod':
        img_name = url.split('/')[-1]
        way = os.path.join("static/img/product/") + f'{img_name}'
    elif data == 'desc':
        link = url.split('foxtrot')
        way = os.path.join('static/img/product') + link[2]

    way_dir = os.path.dirname(way)
    Path(way_dir).mkdir(parents=True, exist_ok=True)
    return way, way.split('static')[1]

@app.task(bind=True, default_retry_delay=300, max_retries=5)
def img_loader(self, url, way):
    try:
        if not os.path.exists(way):
            response = requests.get(url)
            img = response.content
            with open(way, 'wb') as data:
                data.write(img)
    except Exception as e:
        self.retry(e)
