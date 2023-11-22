# Use the official Python image as base image
FROM python:3.7-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

RUN apt-get update

RUN apt-get install -y build-essential cmake

RUN apt-get install -y libopenblas-dev liblapack-dev

RUN apt-get install -y libx11-dev libgtk-3-dev

RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "face_api.py"]
