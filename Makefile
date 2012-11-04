
all:
	

install:
	curl http://peak.telecommunity.com/dist/ez_setup.py | python
	python setup.py install

clean:
	rm -rf dist/ build/ jacot.egg-info

update:
	python2.7 setup.py register
	python2.6 setup.py bdist_egg upload
	python2.7 setup.py bdist_egg upload

