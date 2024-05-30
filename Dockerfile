# Get a base image with a slim version of Python 3.10
FROM python:3.12-slim

# run a pip install for poetry 1.5.0
RUN pip install poetry==1.5.0

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make start_repo_tool.sh executable
RUN chmod +x /app/start_repo_tool.sh

# Install AWS CLI
RUN pip install awscli

# Run poetry install --without dev
RUN poetry install --no-root 

# Expose the port the app runs on
EXPOSE 5000

# Run the start_repo_tool.sh script
# Note: ENTRYPOINT cannot be overriden by docker run command
ENTRYPOINT ["/app/start_repo_tool.sh"]
