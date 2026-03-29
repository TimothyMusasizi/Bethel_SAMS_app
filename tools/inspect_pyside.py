import PySide6
import PySide6.QtWidgets as qw
print('PySide6.__version__ =', getattr(PySide6, '__version__', 'unknown'))
print('QtWidgets module file:', getattr(qw, '__file__', 'n/a'))
print('has QAction attribute:', hasattr(qw, 'QAction'))
print('sample Action names in QtWidgets:', [n for n in dir(qw) if 'Action' in n][:50])
