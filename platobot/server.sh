# for gunicorn
WORKERS=4
TIMEOUT=60
DEBUG=true

LISTENING_IP=0.0.0.0
PORT=5000

function start_server()
{
    echo "starting Server....."
    source activate
    which python
    # if not in debug mode, hide the outputs
    if [ "$1" != true ]; then
        exec >/dev/null
    fi

    gunicorn -w $WORKERS -b $LISTENING_IP:$PORT --timeout $TIMEOUT --log-file=- platobot.bin.web_app:app &
    python -m platobot.bin.workers_dispatcher &
}


function stop_server
{
    pid_list=`ps -ef | grep 'platobot.bin.web_app:ap[p]\|workers_dispatche[r]' | awk '{print $2}'`
    for pid in $pid_list; do
        kill -9 $pid  2>&1 > /dev/null
    done
    echo "stopped server."
}

if [ "$1" == "start" ]; then

    if [ "$2" == "debug" ]; then
        start_server $DEBUG
    else
        start_server
    fi

elif [ "$1" == "stop" ]; then
    stop_server
else
    echo "usage: ./server.sh [start|stop]"

fi