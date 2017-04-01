#!/usr/bin/env python3
#-*- coding: utf-8 -*-
# various tests

import unittest
import os
import json
from sys import exit

import boards as b
import global_vars as g
import post as p


class BoardlistTests(unittest.TestCase):
    root = os.getcwd()
    blist = root + '/boardlist'
    postn = root + '/postnums'

    def setUp(self):
        '''Creates a dummy setup for every test.'''
        g.write_new_settings(self.blist, {})
        g.write_new_settings(self.postn, {})
        try:
            os.mkdir(self.root + '/boards')
        except OSError:
            pass

    def tearDown(self):
        '''Removes dummy files after test is done.'''
        os.remove(self.blist)
        os.remove(self.postn)
        try:
            os.remove(self.root + '/boards/a/index')
            os.rmdir(self.root + '/boards/a')
            os.rmdir(self.root + '/boards')
        except OSError:
            pass

    # actual tests
    def testAddValidBoard(self):
        '''Just adds a valid board name (a string for now).
        Should evaluate to True.'''
        self.assertTrue(b.add_board('a', 'Anime & Manga',
                                    self.blist, self.root, self.postn))

    def testAddInvalidIntegerBoard(self):
        '''Tries to add an invalid board name (an integer).
        Should evaluate to False.'''
        self.assertFalse(b.add_board(5, '', self.blist, self.root, self.postn))

    def testAddInvalidListBoard(self):
        '''Same as above, but tries to add a list with string - just really
        making sure the checks work.'''
        self.assertFalse(b.add_board(
            ['a', ], '', self.blist, self.root, self.postn))

    def testAddSameBoardTwice(self):
        '''Tries to add the same board twice. First try should success and
        evaluate to True, second should fail.'''
        # This will work:
        self.assertTrue(b.add_board(
            'a', '', self.blist, self.root, self.postn))
        # This won't, since we just added a board named like that:
        self.assertFalse(b.add_board(
            'a', '', self.blist, self.root, self.postn))

    def testGetBoardlist(self):
        '''Tests if getting function works properly. Also tests the custom
        description setting in add_board().'''
        self.assertTrue(b.add_board('a', 'Anime & Manga',
                                    self.blist, self.root, self.postn))
        self.assertEqual(b.get_boardlist(self.blist), {'a': 'Anime & Manga'})


class PostingTests(unittest.TestCase):
    root = os.getcwd()
    blist = root + '/boardlist'
    postn = root + '/postnums'

    def setUp(self):
        try:
            os.mkdir(self.root + '/boards')
        except OSError:
            pass
        g.write_new_settings(self.blist, {})
        b.add_board("a", "Anime", self.blist, self.root, self.postn)

    def tearDown(self):
        os.remove(self.blist)
        os.remove(self.postn)
        try:
            os.remove(self.root + '/boards/a/index')
            os.rmdir(self.root + '/boards/a')
            os.rmdir(self.root + '/boards')
        except OSError:
            pass

    def testValidPost(self):
        p.post("a", "test post", "test subject", -1, self.postn, self.root)
        index = b.get_index("a", self.root)
        self.assertEqual(index[0][0], 1)  # assert thread/post ID is correct
        self.assertEqual(index[0][1], "test subject")
        self.assertEqual(index[0][2][2], "test post")

    def testValidReply(self):
        p.post("a", "test post", "test subject", -1, self.postn, self.root)
        p.post("a", "reply", '', 1, self.postn, self.root)
        index = b.get_index("a", self.root)
        self.assertEqual(index[0][3][1], 2)  # assert post ID
        self.assertEqual(index[0][3][2], "reply")

    def testPostWithInvalidArguments(self):
        '''Tries to add a post with integer and list as post_text
        and subject arguments. It should be converted to str and
        added without problem.'''
        p.post("a", 78, 69, -1, self.postn, self.root)
        p.post("a", ["hello", "world"], [
               "sub", "ject"], -1, self.postn, self.root)
        index = b.get_index("a", self.root)
        self.assertEqual(index[0][1], "69")  # subject
        self.assertEqual(index[0][2][2], "78")  # post
        self.assertEqual(index[1][1], "['sub', 'ject']")  # subject
        self.assertEqual(index[1][2][2], "['hello', 'world']")  # post

if __name__ == '__main__':
    # run tests
    unittest.main()
