from distutils.core import setup

setup(name = 'putils',
      version = '0.1',
	  package_dir={"": "putils"},
	  py_modules = ["dfutil", "statsutil", "strutil", "util"])
