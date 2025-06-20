echo hello
sleep 60
sudo pigpiod
sleep 10
sudo python3 rainfall.py &
./collectdata.sh &
