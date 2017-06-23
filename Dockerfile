FROM markadams/chromium-xvfb-py3

WORKDIR /usr/src/app

RUN apt-get remove python-pip

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . /usr/src/app

RUN python3 /usr/src/app/setup.py install

EXPOSE 3000 3001 5901

CMD xvfb-run --server-args="-screen 0 1024x768x24" python3 ./njcampfin/__init__.py Phil Murphy 2017 GOVERNOR


