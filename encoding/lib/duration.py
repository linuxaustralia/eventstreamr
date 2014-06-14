import datetime

def str2delta(raw):
	formats = ["%H:%M:%S", "%H:%M:%S.%f", "%M:%S", "%M:%S.%f"]
	time = None
	zero = datetime.datetime.min
	for f in formats:
		try:
			time = datetime.datetime.strptime(raw, f) - zero
			break
		except ValueError:
			pass
	return time
