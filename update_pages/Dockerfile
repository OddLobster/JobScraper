# Use an official Python runtime as a parent image
FROM python:3.8

# Install necessary dependencies
RUN pip install selenium

# Download and install Chrome and ChromeDriver
RUN apt-get update -qqy \
    && apt-get -qqy install wget unzip \
    && apt-get -qqy install chromium-driver \
    && apt-get -qqy install chromium \
    && rm -rf /var/lib/apt/lists/*



# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app


# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt



# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python3", "page_crawl.py"]
