# Use Python 3.12 image
FROM python:3.12

# Establish working directory
WORKDIR /app

# Copy dependencies file and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy rest of files
COPY . .

# Expose port
EXPOSE 8080

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
