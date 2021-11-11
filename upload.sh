sleep 3600
cd rws-test
while :
do
	git add .
	git commit -m "append data"
	git push
	cd ../RD200P2_UART_DATA
	git add .
	git commit -m "append data"
	git push
	cd ../rws-test
	sleep 3600
done
