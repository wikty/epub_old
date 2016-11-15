# -*- coding:utf-8 -*-
import os, errno, shutil, json, time
from epubMaker.page_generator import PageGenerator
from epubMaker.package_generator import PackageGenerator

class EpubGenerator:
    def __init__(self, bookname, bookcname, bookid, booktype, bookcat, author, publisher, rootpath, jsonfile, coverfile):
        self.bookname = bookname
        self.bookcname = bookcname
        self.bookid = bookid
        self.booktype = booktype if booktype in ['tw', 'zh'] else 'tw'
        self.bookcat = bookcat
        self.author = author
        self.publisher = publisher
        self.rootpath = rootpath.rstrip(os.sep) # without ending '/'
        self.jsonfile = jsonfile # data json filename(should in rootpath director)
        self.coverfile = coverfile # cover image filename(should in rootpath director)
        self.coverpage = 'coverpage.xhtml'
        self.frontpage = 'frontpage.xhtml'
        self.contentspage = 'contents.xhtml'
        self.navpage = 'nav.xhtml'
        self.packagefile = 'package.opf'
        self.ncxfile = 'toc.ncx'
        #self.images = set() # without extend name '.jpg'
        self.articles = []
        self.currentdir = os.path.dirname(os.path.realpath(__file__)).rstrip(os.sep)
        self.metainfdir = ''
        self.xhtmldir = ''
        self.imgdir = ''
        self.jsdir = ''
        self.cssdir = ''
        self.makedirs()
        self.cpyfiles()
        self.covertitle = '封面'
        if self.booktype == 'tw':
            self.contentstitle = '目錄'
            self.fronttitle = '版權信息'
            self.navtitle = '目錄'
        else:
            self.contentstitle = '目录'
            self.fronttitle = '版权信息'
            self.navtitle = '目录'

    def makedirs(self):
        bookname = self.bookname
        rootpath = self.rootpath
        currentdir = self.currentdir

        # create epub resource directories
        self.metainfdir = os.sep.join([rootpath, 'epub', bookname,'META-INF'])
        self.epubdir = os.sep.join([rootpath, 'epub', bookname,'EPUB'])
        self.xhtmldir = os.sep.join([rootpath, 'epub', bookname,'EPUB','xhtml'])
        self.imgdir = os.sep.join([rootpath, 'epub', bookname,'EPUB','img'])
        self.jsdir = os.sep.join([rootpath, 'epub', bookname,'EPUB','js'])
        self.cssdir = os.sep.join([rootpath, 'epub', bookname,'EPUB','css'])
        dirs = [
            self.metainfdir, 
            self.epubdir,
            self.xhtmldir, 
            self.imgdir, 
            self.jsdir, 
            self.cssdir
        ]
        for dirname in dirs:
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def cpyfiles(self):
        currentdir = self.currentdir
        bookname = self.bookname
        rootpath = self.rootpath
        coverfile = self.coverfile
        # copy epub resource files
        shutil.copy(os.sep.join([currentdir, 'epub', 'mimetype']), 
            os.sep.join([rootpath, 'epub', bookname, 'mimetype']))
        shutil.copy(os.sep.join([currentdir, 'epub', 'META-INF', 'container.xml']), 
            os.sep.join([rootpath, 'epub', bookname, 'META-INF', 'container.xml']))
        shutil.copy(os.sep.join([currentdir, 'epub', 'EPUB', 'css', 'main.css']), 
            os.sep.join([rootpath, 'epub', bookname, 'EPUB', 'css', 'main.css']))
        shutil.copy(os.sep.join([rootpath, coverfile]), 
            os.sep.join([rootpath, 'epub', bookname, 'EPUB', 'img', 'cover.jpg']))

    def run(self):
        self.generate_articles()
        self.generate_coverpage()
        self.generate_frontpage()
        self.generate_contentspage()
        self.generate_navpage()
        self.generate_package()
    
    def generate_articles(self):
        jsonfile = os.sep.join([self.rootpath, self.jsonfile])
        # generate xhtml documents
        with open(jsonfile, 'r', encoding='utf-8') as f:
            for line in f:
                article = json.loads(line)
                '''
                article.keys()
                ['en_title', 'en_sub_category', 'filename', 'book', 'en_book', 'conten
t', 'title', 'en_category', 'sub_category', 'category']
                '''
                if not article['filename'] or not article['content']:
                    raise Exception('filename and content must be filled')
                # for key in article:
                #     if key == 'content':
                #         article[key] = '\n'.join(['<p>' + l + '</p>'  for l in article[key]])
                    # elif key == 'comment':
                    #     article[key] = '\n'.join(['<p>' + l + '</p>' for l in article[key]])
                article['content'] = '\n'.join(['<p>' + l + '</p>'  for l in article['content']])
                if 'comment' not in article:
                    article['comment'] = []
                else:
                    article['content'] = article['content'] + '\n<hr/>\n' + '\n'.join(['<p>' + l + '</p>' for l in article['comment']])
                article['contentspage'] = self.contentspage
                self.articles.append(article)

        self.articles.sort(key = lambda item: item['article_id'])
        #self.articles.sort(key=lambda item: item['en_title'].replace('-', ''))
        count = 1
        for article in self.articles:
            if article['article_id'] != count:
                raise Exception('article lost')
            count += 1
            article_file_name = os.sep.join([
                self.xhtmldir,
                '.'.join([article['filename'], 'xhtml'])
            ])

            PageGenerator.generate_article(article_file_name, article)
    
    def generate_coverpage(self):
        cover_file_name = os.sep.join([self.xhtmldir, self.coverpage])
        PageGenerator.generate_coverpage(cover_file_name, {'cover': self.coverfile})

    def generate_frontpage(self):
        front_file_name = os.sep.join([self.xhtmldir, self.frontpage])
        if self.booktype == 'zh':
            shutil.copy(os.sep.join([self.currentdir, 'epub', 'EPUB', 'xhtml', 'frontpage_simplified_ch.xhtml']), front_file_name)
        elif self.booktype == 'tw':
            shutil.copy(os.sep.join([self.currentdir, 'epub', 'EPUB', 'xhtml', 'frontpage_traditional_ch.xhtml']), front_file_name)
        today = time.localtime()
        data = {
            'book_name': self.bookcname,
            'author': self.author,
            'book_category': self.bookcat,
            'publisher': self.publisher,
            'publish_year': str(today.tm_year),
            'book_id': self.bookid,
            'mod_year': str(today.tm_year),
            'mod_month': str(today.tm_mon) if len(str(today.tm_mon)) == 2 else '0'+str(today.tm_mon),
            'mod_day': str(today.tm_mday) if len(str(today.tm_mday)) == 2 else '0'+str(today.tm_mday)
        }
        PageGenerator.generate_frontpage(front_file_name, data)

    def generate_contentspage(self):
        contents_file_name = os.sep.join([self.xhtmldir, self.contentspage])
        menu = []
        for i in range(len(self.articles)):
            article = self.articles[i]
            item = '<p class="sgc-toc-level-1"><a href="{filename}.xhtml" id="{id}">{title}</a></p>'.format(filename=article['filename'], id=article['article_id'], title=article['title']) 
            menu.append(item)

        data = {
            'content': '\n'.join(menu),
            'title': self.contentstitle
        }
        PageGenerator.generate_contentspage(contents_file_name, data)

    def generate_navpage(self):
        menu = []
        for i in range(len(self.articles)):
            article = self.articles[i]
            li = '    <li><a href="{filename}.xhtml">{title}</a></li>'.format(filename=article['filename'], title=article['title'])
            menu.append(li)
        nav_file_name = os.sep.join([self.xhtmldir, self.navpage])
        data = {
            'content': '\n'.join(menu),
            'coverpage': self.coverpage,
            'frontpage': self.frontpage,
            'contentspage': self.contentspage,
            'title': self.navtitle,
            'covertitle': self.covertitle,
            'fronttitle': self.fronttitle,
            'contentstitle': self.contentstitle
        }
        PageGenerator.generate_navpage(nav_file_name, data)

    def generate_package(self):
        package_file_name = os.sep.join([self.epubdir, self.packagefile])
        data = {
            'filename': package_file_name,
            'title': self.bookcname,
            'author': self.author,
            'publisher': self.publisher,
            'bookid': self.bookid,
            'coverfile': self.coverfile,
            'navpage': self.navpage,
            'coverpage': self.coverpage,
            'frontpage': self.frontpage,
            'contentspage': self.contentspage,
            'ncxfile': self.ncxfile,
            'articles': self.articles
        }

        PackageGenerator.generate_opf(**data)
        data = {
            'filename': os.sep.join([self.epubdir, self.ncxfile]),
            'bookid': self.bookid,
            'bookcname': self.bookcname,
            'articles': self.articles,
            'covertitle': self.covertitle,
            'contentstitle': self.contentstitle,
            'fronttitle': self.fronttitle
        }
        PackageGenerator.generate_ncx(**data)