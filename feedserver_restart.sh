echo "Stopping feedserver..."
ps ax | grep python | grep feedserver | grep -v grep | awk {'print $1'} | xargs kill
echo "Starting feedserver..."
echo "executing: python feedserver.py >> feed_forever.log 2>&1 &"
python feedserver.py >>feed_forever.log 2>&1 &
echo "Done"
