# Choose an appropriate base image based on your application framework
# Replace with your preferred Python version if needed
FROM python:3.9-slim  

# Copy your application code into the container
COPY requirements.txt ./
 # Install dependencies
RUN pip install -r requirements.txt 

# Set the working directory where your app code resides
WORKDIR /orders-manager
# Copy your app code into the container
COPY . ./

# Expose any necessary ports (if applicable)
# Replace with the port your app uses
# ENV PORT=8080
# EXPOSE 8000  

# Specify the command to run your app
# Replace with the actual command to start your app
CMD ["python", "main.py"]  
