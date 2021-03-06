#!/usr/bin/env python

import importlib
import sys
import os
import unittest
import socket
import tempfile
import errno
from test import support

TESTFN = support.TESTFN
TESTDIRN = os.path.basename(tempfile.mkdtemp(dir='.'))


class TestSupport(unittest.TestCase):
    def setUp(self):
        support.unlink(TESTFN)
        support.rmtree(TESTDIRN)
    tearDown = setUp

    def test_import_module(self):
        support.import_module("ftplib")
        self.assertRaises(unittest.SkipTest, support.import_module, "foo")

    def test_import_fresh_module(self):
        support.import_fresh_module("ftplib")

    def test_get_attribute(self):
        self.assertEqual(support.get_attribute(self, "test_get_attribute"),
                        self.test_get_attribute)
        self.assertRaises(unittest.SkipTest, support.get_attribute, self, "foo")

    @unittest.skip("failing buildbots")
    def test_get_original_stdout(self):
        self.assertEqual(support.get_original_stdout(), sys.stdout)

    def test_unload(self):
        import sched
        self.assertIn("sched", sys.modules)
        support.unload("sched")
        self.assertNotIn("sched", sys.modules)

    def test_unlink(self):
        with open(TESTFN, "w") as f:
            pass
        support.unlink(TESTFN)
        self.assertFalse(os.path.exists(TESTFN))
        support.unlink(TESTFN)

    def test_rmtree(self):
        os.mkdir(TESTDIRN)
        os.mkdir(os.path.join(TESTDIRN, TESTDIRN))
        support.rmtree(TESTDIRN)
        self.assertFalse(os.path.exists(TESTDIRN))
        support.rmtree(TESTDIRN)

    def test_forget(self):
        mod_filename = TESTFN + '.py'
        with open(mod_filename, 'w') as f:
            print('foo = 1', file=f)
        sys.path.insert(0, os.curdir)
        importlib.invalidate_caches()
        try:
            mod = __import__(TESTFN)
            self.assertIn(TESTFN, sys.modules)

            support.forget(TESTFN)
            self.assertNotIn(TESTFN, sys.modules)
        finally:
            del sys.path[0]
            support.unlink(mod_filename)

    def test_HOST(self):
        s = socket.socket()
        s.bind((support.HOST, 0))
        s.close()

    def test_find_unused_port(self):
        port = support.find_unused_port()
        s = socket.socket()
        s.bind((support.HOST, port))
        s.close()

    def test_bind_port(self):
        s = socket.socket()
        support.bind_port(s)
        s.listen(1)
        s.close()

    def test_temp_cwd(self):
        here = os.getcwd()
        with support.temp_cwd(name=TESTFN):
            self.assertEqual(os.path.basename(os.getcwd()), TESTFN)
        self.assertFalse(os.path.exists(TESTFN))
        self.assertTrue(os.path.basename(os.getcwd()), here)

    def test_sortdict(self):
        self.assertEqual(support.sortdict({3:3, 2:2, 1:1}), "{1: 1, 2: 2, 3: 3}")

    def test_make_bad_fd(self):
        fd = support.make_bad_fd()
        with self.assertRaises(OSError) as cm:
            os.write(fd, b"foo")
        self.assertEqual(cm.exception.errno, errno.EBADF)

    def test_check_syntax_error(self):
        support.check_syntax_error(self, "def class")
        self.assertRaises(AssertionError, support.check_syntax_error, self, "1")

    def test_CleanImport(self):
        import importlib
        with support.CleanImport("asyncore"):
            importlib.import_module("asyncore")

    def test_DirsOnSysPath(self):
        with support.DirsOnSysPath('foo', 'bar'):
            self.assertIn("foo", sys.path)
            self.assertIn("bar", sys.path)
        self.assertNotIn("foo", sys.path)
        self.assertNotIn("bar", sys.path)

    def test_captured_stdout(self):
        with support.captured_stdout() as s:
            print("hello")
        self.assertEqual(s.getvalue(), "hello\n")

    def test_captured_stderr(self):
        with support.captured_stderr() as s:
            print("hello", file=sys.stderr)
        self.assertEqual(s.getvalue(), "hello\n")

    def test_captured_stdin(self):
        with support.captured_stdin() as s:
            print("hello", file=sys.stdin)
        self.assertEqual(s.getvalue(), "hello\n")

    def test_gc_collect(self):
        support.gc_collect()

    def test_python_is_optimized(self):
        self.assertIsInstance(support.python_is_optimized(), bool)

    def test_swap_attr(self):
        class Obj:
            x = 1
        obj = Obj()
        with support.swap_attr(obj, "x", 5):
            self.assertEqual(obj.x, 5)
        self.assertEqual(obj.x, 1)

    def test_swap_item(self):
        D = {"item":1}
        with support.swap_item(D, "item", 5):
            self.assertEqual(D["item"], 5)
        self.assertEqual(D["item"], 1)

    # XXX -follows a list of untested API
    # make_legacy_pyc
    # is_resource_enabled
    # requires
    # fcmp
    # umaks
    # findfile
    # check_warnings
    # EnvironmentVarGuard
    # TransientResource
    # transient_internet
    # run_with_locale
    # set_memlimit
    # bigmemtest
    # precisionbigmemtest
    # bigaddrspacetest
    # requires_resource
    # run_doctest
    # threading_cleanup
    # reap_threads
    # reap_children
    # strip_python_stderr
    # args_from_interpreter_flags
    # can_symlink
    # skip_unless_symlink


def test_main():
    tests = [TestSupport]
    support.run_unittest(*tests)

if __name__ == '__main__':
    test_main()
