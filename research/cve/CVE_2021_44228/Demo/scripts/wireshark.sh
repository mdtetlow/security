docker run -d \
  --name=wireshark \
  --cap-add=NET_ADMIN \
  -e PUID=1000 \
  -e PGID=1000 \
  -e TZ=Europe/London \
  -p 3000:3000 `#optional` \
  -v /wireshark:/config \
  --restart unless-stopped \
  --network demo_log4j \
  lscr.io/linuxserver/wireshark
