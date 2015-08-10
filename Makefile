play_icfp2015:
	pyinstaller --name play_icfp2015 --distpath=. --onefile ./src/clever_solver.py

clean:
	rm play_icfp2015
	rm -r build/
	rm play_icfp2015.spec
