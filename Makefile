make:
	python -OO -m py_compile user.py
	chmod +x user.py
	ln -f user.py user
	
	python -OO -m py_compile cs.py
	chmod +x cs.py
	ln -f cs.py cs
	
	python -OO -m py_compile bs.py
	chmod +x bs.py
	ln -f bs.py bs

clean:
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	rm user
	rm cs
	rm bs