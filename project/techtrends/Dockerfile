# Use a Python base image in version 3.8
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install packages defined in the requirements.txt file
RUN pip install -r requirements.txt

# Copy the entire project directory to the container
COPY . .

# Ensure that the database is initialized with the pre-defined posts
RUN python init_db.py

# Expose the application port 3111
EXPOSE 3111

# Set the command to run the application
CMD ["python", "app.py"]