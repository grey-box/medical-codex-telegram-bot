# Use the official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy the source code to the container
COPY . /app

# # Copy the Pipfile and Pipfile.lock to the container
# COPY Pipfile Pipfile.lock ./

# Install Pipenv and project dependencies
RUN pip install pipenv 

# Install project dependencies using Pipenv
# RUN pipenv --python 3.10
RUN pipenv install --system --deploy --ignore-pipfile

# Start the bot
CMD ["python", "conversation_bot/bot.py"]