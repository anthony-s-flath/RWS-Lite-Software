while :
do
	sudo python3 soilmoist.py
	sudo python3 soiltemp.py
	sudo python3 tph.py
	sudo python3 uv.py
    sudo python3 winddir.py
	sudo python3 windspeed.py
	sleep 600
done
