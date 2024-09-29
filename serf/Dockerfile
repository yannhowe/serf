FROM python:3.13.0rc2
RUN python -m pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
COPY . /usr/src/app/
COPY newswire/static/newswire/cp/fonts/Raleway-*.ttf /usr/share/fonts/TTF/
RUN fc-cache -f -v