FROM ubuntu:latest AS build

RUN apt-get update && apt-get upgrade

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get install -y python3.9
RUN apt install -y python3-pip

RUN apt-get install -y libgl1-mesa-glx

RUN apt-get install -y cmake

RUN pip install -r requirements.txt

COPY . /app/

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "face_api.py"]
