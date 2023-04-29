# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory to /app
WORKDIR /app

# Copy the requirements.txt into the container at /app
COPY apps/processor/requirements.txt /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install extra dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    ghostscript \
    python3-tk \
    poppler-utils \
    libsm6 \
    libxext6 \
    libxrender1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Spacy's en_core_web_sm
RUN python -m spacy download en_core_web_sm

# Copy the New Relic CLI tarball to the Docker container
COPY deps/newrelic-cli_0.67.21_Linux_x86_64.tar.gz /tmp/newrelic-cli.tar.gz

# Install the New Relic CLI
RUN tar -xzf /tmp/newrelic-cli.tar.gz -C /usr/local/bin && \
    rm /tmp/newrelic-cli.tar.gz && \
    chmod +x /usr/local/bin/newrelic

# Set environment variables for New Relic CLI
ENV NEW_RELIC_API_KEY=NRAK-NHVMV1H96OQ9RL45ULPMP3O2T0H \
    NEW_RELIC_ACCOUNT_ID=3914996

# Install New Relic logs-integration
RUN newrelic install -n logs-integration

# Copy the current directory contents into the container at /app
COPY newrelic.ini /app/
COPY ./providers/ /app/providers/
COPY ./messaging/ /app/messaging/
COPY ./extraction/ /app/extraction/
COPY apps/processor/ /app/
COPY processor.py /app/

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Set environment variables
ENV NEW_RELIC_CONFIG_FILE=newrelic.ini

# Run the application
CMD ["newrelic-admin", "run-program", "python", "processor.py"]
