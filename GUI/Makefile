clean:
	rm -rf build || true
	rm -rf dist || true

build: clean
	pyinstaller --onefile --noconsole --icon=icon.png server_setup.py

run:
	./dist/server_setup

