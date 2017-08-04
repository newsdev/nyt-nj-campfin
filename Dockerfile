FROM markadams/chromium-xvfb-py3

WORKDIR /usr/src/app

RUN apt-get remove python-pip

RUN apt-get update && \
  apt-get install libxml2-dev libxslt-dev python-dev lib32z1-dev -y

COPY requirements.txt /usr/src/app/
RUN pip3 install -r /usr/src/app/requirements.txt
COPY . /usr/src/app/

ENV PYTHONPATH=/usr/src/app

RUN mkdir -p /var/www/data

EXPOSE 3000 3001 5901

CMD xvfb-run --server-args="-screen 0 1024x768x24" /usr/bin/python3 /usr/src/app/njcampfin/__init__.py "" "" 2017 GOVERNOR /var/www/data/nj_campfin_governor.json True True > /var/www/data/nj_campfin_governor_output.txt


