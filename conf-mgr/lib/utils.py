

class Observable(object):

  def __init__(self, *args, **kwargs):
    super(Observable, self).__init__(*args, **kwargs)
    # Don't use weakref becuase it will cause race-conditions.
    self.__observers = set()

  def add_observer(self, fn):
    self.__observers.add(fn)

  def remove_observer(self, fn):
    self.__observers.remove(fn)

  def _notify_observers(self, *args, **kwargs):
    for fn in self.__observers:
      fn(*args, **kwargs)
