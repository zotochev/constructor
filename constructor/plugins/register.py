plugins_all = []


def register_plugin(cls):
	global plugins_all
	plugins_all.append(cls)
	return cls
