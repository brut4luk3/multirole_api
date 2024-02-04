# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for Chrome and ChromeDriver
RUN apt-get update && apt-get install -y wget xvfb unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oE "[0-9.]{2,20}." | cut -d '.' -f 1,2,3) \
    && CHROME_DRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/100.0.4896.20/chromedriver_linux64.zip") \
    && wget -N https://chromedriver.storage.googleapis.com/100.0.4896.20/chromedriver_linux64.zip -P /tmp \
    && unzip /tmp/chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver_linux64.zip \
    && chmod 0755 /usr/local/bin/chromedriver

# Copy the local directory contents to the container
COPY . .

# Install any Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available outside this container
EXPOSE 5000

# Define environment variables for headless Chrome
ENV DISPLAY=:99

# Run the command to start xvfb, a virtual frame buffer. This is required for running browsers in headless mode.
RUN Xvfb :99 -screen 0 1024x768x16 &

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]