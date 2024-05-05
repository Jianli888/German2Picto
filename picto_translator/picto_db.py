#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from flask import g 


class PictoDB:
    """
    Class that creates a connection to the pictogram-synset database and that provides methods to search the database.
    """

    def __init__(self,db_file):
        self.db_file = db_file

    def get_conn(self):
            if 'picto_db_conn' not in g:
                g.picto_db_conn = self._create_connection(self.db_file)
            return g.picto_db_conn
    

    @staticmethod
    def _create_connection(db_file):
        """
        Create a read-only connection to a SQLite database.
        """
        path = "file:" + db_file + "?mode=ro"
        conn = sqlite3.connect(path, uri=True)
        return conn

    def check_if_simple_picto(self, synset_id, is_fem=None, is_plur=None):
        """
        Returns the picto path corresponding to the synset ID from the simple_pictos table if it exists. There can be
        only one result since the synset ID is the table's key. Returns female or plural picto version if necessary.
        """
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT p.picto_id, p.path FROM pictos p, simple_pictos s WHERE s.synset_id=? AND s.picto_id = p.picto_id",
                    (synset_id,))
        simple_row = cur.fetchone()
        if simple_row:
            picto_id = simple_row[0]
            picto_path = simple_row[1]
            bw_picto_path = self.get_bw_picto(picto_id)

            # check for female / plural pictos
            if is_fem:
                cur.execute("SELECT female_picto_id FROM gendered_pictos WHERE male_picto_id=?", (picto_id,))
                gender_row = cur.fetchone()
                if gender_row:
                    female_picto_id = gender_row[0]
                    cur.execute('SELECT path FROM pictos WHERE picto_id=?', (female_picto_id,))
                    picto_path = cur.fetchone()[0]
                    bw_picto_path = self.get_bw_picto(female_picto_id)

            if is_plur:
                cur.execute("SELECT plural_picto_id FROM numbered_pictos WHERE singular_picto_id=?", (picto_id,))
                number_row = cur.fetchone()
                if number_row:
                    plural_picto_id = number_row[0]
                    cur.execute('SELECT path FROM pictos WHERE picto_id=?', (plural_picto_id,))
                    picto_path = cur.fetchone()[0]
                    bw_picto_path = self.get_bw_picto(plural_picto_id)
        else:
            picto_path, bw_picto_path = None, None

        return picto_path, bw_picto_path

    def check_if_synset_in_complex(self, synset_id):
        """
        Returns the rows corresponding to the head_synset IDs from the complex_pictos table if there exist any.
        """
        Conn = self.get_conn()
        cur = Conn.cursor()
        cur.execute(
            "SELECT c.head_synset_id, c.dependent_synset_id, p.path, p.picto_id FROM pictos p, complex_pictos c WHERE c.head_synset_id = ? AND c.picto_id = p.picto_id",
            (synset_id,))
        rows = cur.fetchall()
        return rows

    def get_bw_picto(self, picto_id):
        """
        Returns black-and-white version of coloured picto with picto_id if available.
        """
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT p.path FROM pictos p, bw_colour_pictos bw WHERE bw.colour_picto_id=? AND bw.bw_picto_id = p.picto_id",
                    (picto_id,))
        bw_row = cur.fetchone()
        if bw_row:
            bw_picto_path = bw_row[0]
            return bw_picto_path
        else:
            return None
        
    @staticmethod
    def close_conn():
        if 'picto_db_conn' in g:
            g.picto_db_conn.close()
            g.pop('picto_db_conn')
