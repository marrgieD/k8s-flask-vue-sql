FROM python:3-alpine3.13
WORKDIR /app     
COPY . /app 
VOLUME /logs
VOLUME /images
RUN pip install -r requirements.txt
COPY core.py /usr/local/lib/python3.10/site-packages/flask_cors/core.py
EXPOSE 5001
CMD ["python","./app.py"]
