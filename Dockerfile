###########
# BUILDER #
###########

# pull official base image
FROM python:3.9.12-alpine as builder

# set work directory
WORKDIR /srv/calltouch_proxy

RUN apk update \
    && apk add gcc python3-dev musl-dev libc-dev libffi-dev

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /srv/calltouch_proxy/wheels -r requirements.txt

#########
# FINAL #
#########

# pull official base image
FROM python:3.9.12-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq
COPY --from=builder /srv/calltouch_proxy/wheels /wheels
COPY --from=builder /srv/calltouch_proxy/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app
