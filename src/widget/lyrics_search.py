#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011~2012 Deepin, Inc.
#               2011~2012 Hou Shaohui
#
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gtk
import os
import gobject
from dtk.ui.button import Button
from dtk.ui.entry import Entry
from dtk.ui.utils import get_content_size
from dtk.ui.threads import post_gui
from dtk.ui.constant import ALIGN_END
from constant import DEFAULT_FONT_SIZE
from dtk.ui.listview import ListView, render_text
from dtk.ui.scrolled_window import ScrolledWindow
from widget.ui import NormalWindow, app_theme
from lrc_download import ttplayer_engine, soso_engine, duomi_engine
from lrc_manager import lrc_manager
from player import Player
from config import config
import utils


class SearchUI(NormalWindow, gobject.GObject):
    __gsignals__ = {"finish" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))}
    
    def __init__(self):
        NormalWindow.__init__(self)
        gobject.GObject.__init__(self)
        self.window.background_dpixbuf = app_theme.get_pixbuf("skin/main.png")
        self.artist_entry = Entry()
        self.artist_entry.set_size_request(120, 25)
        self.title_entry = Entry()
        self.title_entry.set_size_request(120, 25)
        artist_label = gtk.Label()
        artist_label.set_markup("<span color=\"black\">%s</span>" % "艺术家:")
        title_label = gtk.Label()
        title_label.set_markup("<span color=\"black\">%s</span>" % "歌曲:")
        right_align = gtk.Alignment()
        right_align.set(0, 0, 0, 1)
        
        search_button = Button("搜索")
        search_button.connect("clicked", self.search_lyric_cb)
        
        info_box = gtk.HBox(spacing=10)
        title_box = gtk.HBox(spacing=5)        
        title_box.pack_start(title_label, False, False)
        title_box.pack_start(self.title_entry, False, False)
        artist_box = gtk.HBox(spacing=5)
        artist_box.pack_start(artist_label, False, False)
        artist_box.pack_start(self.artist_entry, False, False)
        
        info_box.pack_start(title_box, False, False)
        info_box.pack_start(artist_box, False, False)
        info_box.pack_start(right_align, True, True)
        info_box.pack_start(search_button, False, False)
        
        scrolled_window = ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sort_items = [(lambda item: item.title, cmp), (lambda item: item.artist, cmp)]
        self.result_view = ListView(sort_items)
        self.result_view.connect("double-click-item", self.double_click_cb)
        self.result_view.add_titles(["歌曲名", "艺术家"])
        scrolled_window.add_child(self.result_view)
        
        self.prompt_label = gtk.Label()
        self.prompt_label.set_alignment(0.0, 0.5)
        self.prompt_label.set_size_request(-1, -1)
        left_align = gtk.Alignment()
        left_align.set(0, 0, 0, 1)
        bottom_box = gtk.HBox(spacing=10)
        download_button = Button("下载")
        download_button.connect("clicked", self.download_lyric_cb)
        cancel_button = Button("取消")
        cancel_button.connect("clicked", lambda w: self.hide_window())

        bottom_box.pack_start(self.prompt_label, False, False)
        bottom_box.pack_start(left_align, True, True)
        bottom_box.pack_start(download_button, False, False)
        bottom_box.pack_start(cancel_button, False, False)
        self.window.set_size_request(460, 300)
        
        self.main_box.pack_start(info_box, False, False)
        self.main_box.pack_start(scrolled_window, True, True)
        self.main_box.pack_start(bottom_box, False, False)
        
        self.net_encode = None
        
    def double_click_cb(self, widget, item, colume, x, y):   
        self.download_lyric_cb(widget)
        
    def search_engine(self, artist, title):    
        ttplayer_result = ttplayer_engine.request(artist, title)
        if ttplayer_result:
            self.net_encode = None
            return ttplayer_result
        
        duomi_result = soso_engine.request(artist, title)
        if duomi_result:
            self.net_encode = "gbk"
            return duomi_result
        
        soso_result = soso_engine.request(artist, title)
        if soso_result:
            self.net_encode = "gb18030"
            return soso_result
        return None
        
    def search_lyric_cb(self, widget):
        artist = self.artist_entry.get_text()
        title = self.title_entry.get_text()
        self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "正在搜索歌词文件")
        if artist == "" and title == "":
            self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "囧!没有找到!")
            return
        utils.ThreadRun(self.search_engine, self.render_lyrics, [artist, title]).start()
        
    @post_gui
    def render_lyrics(self, result):
        '''docs'''
        self.result_view.clear()
        if result != None:
            items = [SearchItem(each_info) for each_info in result]
            self.result_view.add_items(items)
            self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "找到%d个歌词 :)" % len(result))
        else:    
            self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "囧!没有找到!")
        

    def download_lyric_cb(self, widget):
        self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "正在下载歌词文件")
        select_items = self.result_view.select_rows
        save_filepath = lrc_manager.get_lrc_filepath(Player.song)
        if len(select_items) > 0:
            url = self.result_view.items[select_items[0]].get_url()
            utils.ThreadRun(utils.download, self.render_download, [url, save_filepath, self.soso_encode]).start()
            
    @post_gui        
    def render_download(self, result):
        if result:
            self.emit("finish", Player.song)
            self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "文件已保存到 %s" % config.get("lyrics", "save_lrc_path"))
        else:    
            self.prompt_label.set_markup("<span color=\"white\">   %s</span>" % "囧! 下载失败!")
        
search_ui = SearchUI()            
        
class SearchItem(gobject.GObject):        
    
    __gsignals__ = {"redraw-request" : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()), }

    def __init__(self, lrc_list):
        super(SearchItem, self).__init__()
        self.update(lrc_list)
        
    def set_index(self, index):    
        self.index = index
        
    def get_index(self):    
        return self.index
    
    def emit_redraw_request(self):
        self.emit("redraw-request")
    
    def update(self, lrc_list):    
        self.__url = lrc_list[2]
        self.title  = lrc_list[1]
        self.artist = lrc_list[0]
        
        # Calculate item size.
        self.title_padding_x = 10
        self.title_padding_y = 5
        (self.title_width, self.title_height) = get_content_size(self.title, DEFAULT_FONT_SIZE)
        
        self.artist_padding_x = 10
        self.artist_padding_y = 5
        (self.artist_width, self.artist_height) = get_content_size(self.artist, DEFAULT_FONT_SIZE)
        
    def render_title(self, cr, rect):
        '''Render title.'''
        rect.x += self.title_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.title, font_size=DEFAULT_FONT_SIZE)
    
    def render_artist(self, cr, rect):
        '''Render artist.'''
        rect.x += self.artist_padding_x
        rect.width -= self.title_padding_x * 2
        render_text(cr, rect, self.artist, font_size = DEFAULT_FONT_SIZE)
        
    def get_column_sizes(self):
        '''Get sizes.'''
        return [(min(self.title_width + self.title_padding_x * 2, 120),
                 self.title_height + self.title_padding_y * 2),
                (min(self.artist_width + self.artist_padding_x * 2, 100),
                 self.artist_height + self.artist_padding_y * 2)
                ]    
    
    def get_renders(self):
        '''Get render callbacks.'''
        return [self.render_title,
                self.render_artist]
    
    def get_url(self):
        return self.__url
