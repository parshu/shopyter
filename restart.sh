echo "Stopping server..."
ps ax | grep python | grep main | grep -v grep | awk {'print $1'} | xargs kill
echo "Starting server..."
echo "executing: python main.py >>forever.log 2>&1 &"
python main.py >>forever.log 2>&1 &
echo "Done"
