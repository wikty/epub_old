# -*- coding:utf-8 -*-
import os, time

from .utils import articleid2filename, chapterid2filename

class PackageGenerator():
    def __init__(self, targetdir, extra):
        targetdir = targetdir.rstrip(os.sep)
        if not os.path.exists(targetdir):
          raise Exception('package directory {} not existed'.format(targetdir))
        self.targetdir = targetdir
        self.xhtmldir = 'xhtml/'
        self.imgdir = 'img/'
        self.cssdir = 'css/'
        self.jsdir = 'js/'
        self.packagefile = extra['packagefile']
        self.ncxfile = extra['ncxfile']
        self.navpage = self.xhtmldir+extra['navpage']
        self.coverpage = self.xhtmldir+extra['coverpage']
        self.frontpage = self.xhtmldir+extra['frontpage']
        self.contentspage = self.xhtmldir+extra['contentspage']
        self.maincssfile = self.cssdir+extra['maincssfile']
        self.coverfile = self.imgdir+extra['coverfile']
        self.booktype = extra['booktype']
        self.bookid = extra['bookid']
        self.bookcname = extra['bookcname']
        self.author = extra['author']
        self.publisher = extra['publisher']

    def now(self, fmt='%Y-%m-%dT%H:%M:%SZ'):
        return time.strftime(fmt, time.localtime(time.time()))

    def get_item_tpl(self, filename, id, mediatype, properties=''):
        if properties:
            return '      <item href="{filename}" id="{id}" media-type="{mediatype}" properties="{properties}" />'.format(filename=filename, id=id, mediatype=mediatype, properties=properties)
        else:
            return '      <item href="{filename}" id="{id}" media-type="{mediatype}" />'.format(filename=filename, id=id, mediatype=mediatype)

    def get_item_ncx(self, filename, id):
        return self.get_item_tpl(filename, id, 'application/x-dtbncx+xml')

    def get_item_nav(self, filename, id):
        return self.get_item_tpl(filename, id, 'application/xhtml+xml', 'nav')

    def get_item_xhtml(self, filename, id):
        return self.get_item_tpl(filename, id, 'application/xhtml+xml')

    def get_item_css(self, filename, id):
        return self.get_item_tpl(filename, id, 'text/css')

    def get_item_img(self, filename, id):
        return self.get_item_tpl(filename, id, 'image/jpeg')

    def get_item_js(self, filename, id):
        return self.get_item_tpl(filename, id, 'text/javascript')

    def get_itemref(self, id, linear='yes'):
        if linear not in ['yes', 'no']:
            linear = 'yes'
        return '      <itemref idref="{id}" linear="{linear}"/>'.format(id=id, linear=linear)

    def get_navpoint(self, id, title, filename):
        playorder = id
        return """
    <navPoint id="navPoint-{id}" playOrder="{playorder}">
      <navLabel>
        <text>{title}</text>
      </navLabel>
      <content src="{filename}" />
    </navPoint>""".format(id=id, title=title, playorder=playorder, filename=filename)

    def generate_opf(self, articles, chapters, tpl):
        filename  = os.sep.join([self.targetdir, self.packagefile])
        
        with open(filename, 'w', encoding='utf-8') as f:
            items = []
            itemrefs = []
            
            items.append(self.get_item_ncx(filename=self.ncxfile, id='ncx'))
            items.append(self.get_item_img(filename=self.coverfile, id='cover.jpg'))
            items.append(self.get_item_css(filename=self.maincssfile, id='main.css'))
            
            nav_id = 'nav'
            items.append(self.get_item_nav(filename=self.navpage, id=nav_id))
            
            coverpage_id = 'coverpage'
            items.append(self.get_item_xhtml(filename=self.coverpage, id=coverpage_id))
            itemrefs.append(self.get_itemref(id=coverpage_id))
            
            frontpage_id = 'frontpage'
            items.append(self.get_item_xhtml(filename=self.frontpage, id=frontpage_id))
            itemrefs.append(self.get_itemref(id=frontpage_id))
            
            contentspage_id = 'contentspage'
            items.append(self.get_item_xhtml(filename=self.contentspage, id=contentspage_id))
            itemrefs.append(self.get_itemref(id=contentspage_id))

            for article_id, article_title in articles:
                article_id = articleid2filename(article_id, self.booktype)
                article_filename = self.xhtmldir+article_id
                items.append(self.get_item_xhtml(filename=article_filename, id=article_id))
                itemrefs.append(self.get_itemref(id=article_id))
            
            if chapters:
                for chapter_id, chapter_title, chapter_articles in chapters:
                    chapter_id = chapterid2filename(chapter_id, self.booktype)
                    chapter_filename = self.xhtmldir+chapter_id
                    items.append(self.get_item_xhtml(filename=chapter_filename, id=chapter_id))
                    itemrefs.append(self.get_itemref(id=chapter_id))

            fields = {
                'bookid': self.bookid,
                'title': self.bookcname,
                'author': self.author,
                'publisher': self.publisher,
                'datetime': self.now(),
                'items': '\n'.join(items),
                'itemrefs': '\n'.join(itemrefs),
                'coverpage': self.coverpage
            }
            f.write(tpl.format(fields))
        return filename

    def generate_ncx(self, articles, chapters, tpl):
        filename  = os.sep.join([self.targetdir, self.ncxfile])
        
        with open(filename, 'w', encoding='utf-8') as f:
            navpoints = []
            count = 1
            if chapters:
                for chapter_id, chapter_title, chapter_articles in chapters:
                    chapter_filename = chapterid2filename(chapter_id, self.booktype)
                    chapter_filename = self.xhtmldir+chapter_filename
                    np = self.get_navpoint(count, chapter_title, chapter_filename)
                    navpoints.append(np)
                    count += 1

                    for article_id in chapter_articles:
                        for artid, arttitle in articles:
                            if artid == article_id:
                                article_filename = articleid2filename(artid, self.booktype)
                                article_filename = self.xhtmldir+article_filename
                                np = self.get_navpoint(count, arttitle, article_filename)
                                navpoints.append(np)
                                count += 1
            else:
                for article_id, article_title in articles:
                    article_filename = articleid2filename(count, self.booktype)
                    article_filename = self.xhtmldir+article_filename
                    np = self.get_navpoint(count, article_title, article_filename)
                    navpoints.append(np)
                    count += 1

            fields = {
                'bookid':self.bookid,
                'title': self.bookcname,
                'navpoints': '\n'.join(navpoints)
            }

            f.write(tpl.format(fields))
        return filename