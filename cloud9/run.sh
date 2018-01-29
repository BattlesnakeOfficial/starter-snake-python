cd ..
echo -e "\n===== https://$C9_HOSTNAME =====\n"
gunicorn app.main:application --access-logfile - --worker-class gevent --bind "$IP:$PORT"
