

big-wave:
	python ./api/main.py

runnit:
	python ./api/server.py &
	cd frontend && npm run dev