pid_list=`ps -ef | grep 'platobot.bin.web_ap[p]\|workers_dispatche[r]' | awk '{print $2}'`
for pid in $pid_list; do
    kill -9 $pid  2>&1 > /dev/null
done
echo "stopped server."