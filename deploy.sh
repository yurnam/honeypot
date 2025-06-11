#!/bin/bash

# CONFIG
SERVER=root@cloud.digikex.com
APP_NAME=honeypot
IMAGE_NAME=honeypot-app
REMOTE_IMAGE_FILE=${IMAGE_NAME}.tar
pip freeze > requirements.txt
echo "==> Building Docker image locally (with sudo)..."
sudo docker build -t $IMAGE_NAME .

echo "==> Saving Docker image to tarball (with sudo)..."
sudo docker save $IMAGE_NAME -o $REMOTE_IMAGE_FILE
sudo chown $USER:$USER $REMOTE_IMAGE_FILE


echo "==> Copying image to remote server ($SERVER)..."
scp $REMOTE_IMAGE_FILE $SERVER:/tmp/

echo "==> Loading image and restarting container on remote server ($SERVER)..."
ssh $SERVER << EOF
  echo "==> Loading Docker image (with sudo)..."
  sudo docker load -i /tmp/$REMOTE_IMAGE_FILE
  rm /tmp/$REMOTE_IMAGE_FILE

  echo "==> Stopping old container (if running)..."
  sudo docker stop $APP_NAME || true
  sudo docker rm $APP_NAME || true

  echo "==> Running new container on port 80 (with sudo)..."
  sudo docker run -d --name $APP_NAME -p 80:80 -p 2222:2222 -p 21:21 -p 25:25 -p 443:443 -p 3306:3306 -p 9100:9100 -p 1183:1183 -p 5060:5060/udp -p 161:161/udp -p 3389:3389 -p 5900:5900 -p 23:23 --restart unless-stopped $IMAGE_NAME

  echo "==> Cleanup complete."
EOF

echo "==> Deployment complete! App should now be running on http://cloud.digikex.com/"

# Optional: uncomment this to show logs automatically
# echo "==> Showing logs:"
# ssh $SERVER "sudo docker logs -f $APP_NAME"
