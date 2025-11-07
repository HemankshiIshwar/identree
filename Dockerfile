# Use a stable, compatible version of Python
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Expose the port your Flask app runs on
EXPOSE 9000

# Set the default command to run your app
CMD ["python", "identree_app.py"]
