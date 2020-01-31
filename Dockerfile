#FROM python:3.6
#
#ENV PYTHONUNBUFFERED 1
#
## Install dependencies in one single command/layer
#RUN apt-get update && apt-get install -y \
#    libffi-dev \
#    libssl-dev \
#    sqlite3 \
#    libjpeg-dev \
#    libopenjp2-7-dev \
#    locales \
#    cron \
#    postgresql-client \
#    gettext \
#    python3-dev \
#    libgdal-dev \
#    git mc python3-venv python3-dev screen build-essential python-dev python-pip python3-pip
#    #&&   apt-get clean  && rm -rf /var/lib/apt/lists*
#
## Add requirements and install them. We do this unnecessasy rebuilding.
#ADD requirements.txt /
#RUN pip install -U pip && pip install -r requirements.txt
## RUN pip install git+https://github.com/deschler/django-modeltranslation.git
#
#WORKDIR /srv/site
#
#EXPOSE 8000
#
#CMD python manage.py runserver 0.0.0.0:8000

FROM python:3.6
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ADD requirements.txt /
RUN pip install -U pip && pip install -r requirements.txt
WORKDIR /srv/site
EXPOSE 8000
CMD python manage.py runserver 0.0.0.0:8000
