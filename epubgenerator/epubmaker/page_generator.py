# -*- coding:utf-8 -*-
import os
from .utils import chapterid2filename, articleid2filename

class PageGenerator():

    def __init__(self, targetdir, extra):
        if not os.path.exists(targetdir):
            raise Exception('target directory {} not existed'.format(targetdir))
        targetdir = targetdir.rstrip(os.sep)

        self.targetdir = targetdir
        self.booktype = extra['booktype']
        self.coverpage = extra['coverpage']
        self.frontpage = extra['frontpage']
        self.contentspage = extra['contentspage']
        self.navpage = extra['navpage']
        self.coverfile = extra['coverfile']
        self.maincssfile = extra['maincssfile']
        self.covertitle = extra['covertitle']
        self.fronttitle = extra['fronttitle']
        self.contentstitle = extra['contentstitle']
        self.navtitle = extra['navtitle']
        self.article_id_prefix = extra['article_id_prefix']
        self.chapter_id_prefix = extra['chapter_id_prefix']

    def get_navpage_li(self, filename, title):
        return '    <li><a href="{filename}">{title}</a></li>'.format(
            filename=filename, 
            title=title)

    def get_contentspage_p(self, level, filename, id_prefix, id, title):
        return '<p class="sgc-toc-level-{level}"><a href="{filename}" id="{id_prefix}{id}">{title}</a></p>'.format(
            level=level,
            filename=filename,
            id_prefix=id_prefix,
            id=id,
            title=title)

    def generate_article(self, article, tpl):
        filename = articleid2filename(article['id'], self.booktype)
        filename = os.sep.join([self.targetdir, filename])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'article_id': article['id'],
                'article_id_prefix': self.article_id_prefix,
                'title': article['title'],
                'content': article['body'],
                'maincssfile': self.maincssfile,
                'contentspage': self.contentspage
            }))
        return filename

    def generate_chapter(self, chapter, tpl):
        filename = chapterid2filename(chapter['id'], self.booktype)
        filename = os.sep.join([self.targetdir, filename])

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'chapter_id': chapter['id'],
                'chapter_id_prefix': self.chapter_id_prefix,
                'title': chapter['title'],
                'maincssfile': self.maincssfile,
                'contentspage': self.contentspage
            }))
        return filename

    def generate_coverpage(self, tpl):
        filename = os.sep.join([self.targetdir, self.coverpage])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tpl.format({
                'coverfile': self.coverfile,
                'title': self.covertitle
            }))
        return filename

    def generate_frontpage(self, bookinfo, tpl):
        filename = os.sep.join([self.targetdir, self.frontpage])
        
        with open(filename, 'w', encoding='utf-8') as f:
            fields = {
                'maincssfile': self.maincssfile,
                'title': self.fronttitle,
                'book_name': bookinfo['bookcname'],
                'book_category': bookinfo['bookcat'],
                'author': bookinfo['author'],
                'publish_year': bookinfo['publish_year'],
                'bookid': bookinfo['bookid'],
                'modify_year': bookinfo['modify_year'],
                'modify_month': bookinfo['modify_month'],
                'modify_day': bookinfo['modify_day']
            }
            f.write(tpl.format(fields))
        return filename

    def generate_navpage(self, articles, chapters, tpl):
        filename = os.sep.join([self.targetdir, self.navpage])
        
        with open(filename, 'w', encoding='utf-8') as f:
            if chapters:
                l = []
                for chapid, chaptitle, chap_articles in chapters:
                    chapfile = chapterid2filename(chapid, self.booktype)
                    li = self.get_navpage_li(chapfile, chaptitle)
                    l.append(li)
                    for article_id in chap_articles:
                        found = False
                        artfile = articleid2filename(article_id, self.booktype)
                        for artid, arttitle in articles:
                            if artid == article_id:
                                found = True
                                break
                        if not found:
                            arttitle = 'None'
                        li = self.get_navpage_li(artfile, arttitle)
                        l.append(li)
            else:
                l = []
                for artid, arttitle in articles:
                    artfile = articleid2filename(artid, self.booktype)
                    li = self.get_navpage_li(artfile, arttitle)
                    l.append(li)
            content = '\n'.join(l)
            f.write(tpl.format({
                'maincssfile': self.maincssfile,
                'title': self.navtitle,
                'content': content,
                'covertitle': self.covertitle,
                'contentstitle': self.contentstitle,
                'fronttitle': self.fronttitle,
                'coverpage': self.coverpage,
                'frontpage': self.frontpage,
                'contentspage': self.contentspage
            }))
        return filename

    def generate_contentspage(self, articles, chapters, tpl):
        filename = os.sep.join([self.targetdir, self.contentspage])
        
        with open(filename, 'w', encoding='utf-8') as f:
            if chapters:
                l = []
                for chapid, chaptitle, chap_articles in chapters:
                    chapfile = chapterid2filename(chapid, self.booktype)
                    p = self.get_contentspage_p(1, chapfile, self.chapter_id_prefix, chapid, chaptitle)
                    l.append(p)
                    for article_id in chap_articles:
                        artfile = articleid2filename(article_id, self.booktype)
                        found = False
                        for artid, arttitle in articles:
                            if artid == article_id:
                                found = True        
                                break
                        if not found:
                            arttitle = 'None'
                        p = self.get_contentspage_p(2, artfile, self.article_id_prefix, article_id, arttitle)
                        l.append(p)
            else:
                l = []
                for artid, arttitle in articles:
                    artfile = articleid2filename(artid, self.booktype)
                    p = self.get_contentspage_p(1, artfile, self.article_id_prefix, artid, arttitle)
                    l.append(p)
            content = '\n'.join(l)
            f.write(tpl.format({
                'maincssfile': self.maincssfile,
                'title': self.contentstitle,
                'content': content
            }))
        return filename