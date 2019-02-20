cd /home/pi/eyic/mjpg-streamer-master/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.

./mjpg_streamer -o "output_http.so -w ./www" -i "input_raspicam.so"
