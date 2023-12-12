FROM mysql:5.6
RUN mkdir /0 
COPY ./store.sql /0 
RUN chmod 777 /0/store.sql
RUN chmod 777 /var/lib/mysql
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone
