py_exec('import sys')
py_exec('sys.path.append(".")')
x = 'Foo';
py_funcall('tests', 'test_char', x); disp(x);
