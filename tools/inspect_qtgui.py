import PySide6
import PySide6.QtGui as qg
print('module file:', qg.__file__)
print('has QAction:', hasattr(qg, 'QAction'))
print('names containing Action:', [n for n in dir(qg) if 'Action' in n][:50])
