# Step 1: Use the official Python image as the base image
FROM python:3.10-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the Python app requirements
COPY requirements.txt .

# Step 4: Install Python dependencies
RUN pip install -r requirements.txt

# Step 5: Copy the entire project to the container
COPY . .

# Step 6: Expose the port Flask will run on
EXPOSE 5000

# Step 7: Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Step 8: Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0"]
