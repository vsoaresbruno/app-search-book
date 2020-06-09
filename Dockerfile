FROM python:3

ENV PYTHONDONTWRITEBYTECODE=True
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app
#VOLUME ["/usr/src/app"]

# We copy the requirements.txt file first to avoid cache invalidations
COPY requirements.txt /usr/src/app/
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
COPY . /usr/src/app
EXPOSE 5000
CMD ["python", "application.py"]
