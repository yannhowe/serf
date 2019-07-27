#!/bin/bash

DATE=`date +%Y-%m-%d-%H-%M-%S`

case "$1" in
        start)
            docker-compose build
            docker-compose up -d
            docker-compose ps
            ;;
        stop)
            docker-compose down
            docker-compose ps
            ;;
        restart)
            docker-compose down
            docker-compose build
            docker-compose up -d
            docker-compose ps
            ;;
        rebuild)
            docker-compose down
            docker-compose build --no-cache
            docker-compose up -d
            docker-compose ps
            ;;
        dev)
            docker-compose down
            docker-compose build --no-cache
            docker-compose -f docker-compose.dev.yml up -d
            docker-compose ps
            ;;
        status)
            docker-compose ps
            ;;
        clean)
            # Script from here https://lebkowski.name/docker-volumes/
            # remove exited containers:
            docker ps --filter status=dead --filter status=exited -aq | xargs -r docker rm -v
            # remove unused images:
            docker images --no-trunc | grep '<none>' | awk '{ print $3 }' | xargs -r docker rmi
            # remove unused volumes:
            find '/var/lib/docker/volumes/' -mindepth 1 -maxdepth 1 -type d | grep -vFf <(docker ps -aq | xargs docker inspect | jq -r '.[] | .Mounts | .[] | .Name | select(.)') | xargs -r rm -fr
            ;;
        nuke)
            docker stop $(docker ps -a -q)
            docker rm $(docker ps -a -q)
            docker rmi $(docker images -a)
            docker volume rm $(docker volume ls |awk '{print $2}')
            ;;
        init)
            echo running migrations....
            docker-compose run --rm serf python manage.py migrate
            echo creating superuser
            docker-compose run --rm serf python manage.py createsuperuser --email admin@gbm.sg --username admin
            echo loading initial data into database
            docker-compose run --rm serf python manage.py loaddata initial_data.json
            ;;
        migrate)
            docker-compose run --rm serf python manage.py makemigrations
            docker-compose run --rm serf python manage.py migrate
            ;;
        dump_dev)
            pg_dump -v -a -h preview.gbm.sg -Fc -o -U postgres postgres > prod_db.$DATE.data.dump
            pg_dump -v -s -h preview.gbm.sg -Fc -o -U postgres postgres > prod_db.$DATE.schema.dump
            pg_dump -v -h preview.gbm.sg -Fc -o -U postgres postgres > prod_db.$DATE.full.dump
            ;;
        dump_live)
            #pg_dump -v -a -h gbm.sg -Fc -o -U postgres postgres > prod_db.$DATE.data.dump
            #pg_dump -v -s -h gbm.sg -Fc -o -U postgres postgres > prod_db.$DATE.schema.dump
            pg_dump -v -h gbm.sg -Fc -o -U postgres postgres > prod_db.$DATE.full.dump
            ;;
        clone_live_json)
            docker-compose run --rm serf python manage.py dumpdata > live_data.json
            ;;
        *)
            echo $"Usage: $0 {start|stop|restart|rebuild|dev|status|clean|nuke|init|migrate|dump_live|dump_live_json}"
            exit 1
date
esac