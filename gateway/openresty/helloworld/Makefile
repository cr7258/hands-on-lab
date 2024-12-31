run:
	mkdir logs
	openresty -p `pwd` -c conf/nginx.conf

stop:
	openresty -p `pwd` -s stop
	rm -rf logs
