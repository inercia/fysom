
all:	egg

clean:
	rm -rf build dist *.egg-info

egg:
	python setup.py bdist_egg
    
