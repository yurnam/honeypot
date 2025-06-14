FROM python:3.11-slim

# Prevent writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Expose port 80 and 22(internal to container)
EXPOSE 80
EXPOSE 22
EXPOSE 2222
EXPOSE 587
EXPOSE 465
EXPOSE 143
EXPOSE 21
EXPOSE 23
EXPOSE 25
EXPOSE 443
EXPOSE 3306
EXPOSE 9100
EXPOSE 3389
EXPOSE 5900
EXPOSE 1883
EXPOSE 161/udp
EXPOSE 5060/udp

# Run Flask app on port 80
CMD ["python", "app.py"]
