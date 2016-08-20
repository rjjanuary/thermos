#!/bin/bash

web_host=localhost;
while true; do
  curl http://$web_host/bookmarks/user/user1 > /dev/null;
  curl http://$web_host/bookmarks/user/user2 > /dev/null;
  curl http://$web_host/bookmarks/user/user3 > /dev/null;
  curl http://$web_host/bookmarks/user/user4 > /dev/null;
  curl http://$web_host/bookmarks/user/user99999 > /dev/null;
done