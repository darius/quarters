opdefs.py: instructions make_opdefs.py
	python make_opdefs.py

meta.obj: meta.asm assemble.py opdefs.py obj_format.py
	python assemble.py <meta.asm >meta.obj

