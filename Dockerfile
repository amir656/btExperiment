FROM python:2.7

ADD BitTornado/ /BitTornado
ADD *.py /
ADD *.sh /
RUN echo "Hello World" > a.txt
RUN python murder_make_torrent.py a.txt localhost:8998 a.torrent
