# -*- coding:utf-8 -*-
import os, json, time
from epubMaker.page_generator import PageGenerator
from epubMaker.package_generator import PackageGenerator
from epubMaker.epub_source import SourceSetup
from epubMaker.chapter import ChapterRaw
from epubMaker.article import ArticleRaw
from epubMaker.template_manager import TplSimpleManager

class EpubGenerator:

    def __init__(self, config):
        # initial: make directories and copy files
        SourceSetup.run(
            config.get_target_epub_dirs(), 
            config.get_target_epub_files(), 
            config.get_source_epub_files()
        )

        self.config = config
        # standalone means that the book don't have chapters
        self.isstandalone = config.is_standalone_book()
        if not self.isstandalone:
            self.chapterid_list = config.get_chapter_id()

        # data source
        self.jsonfile = config.get_source_data_filename('jsonfile')
        self.metafile = config.get_source_data_filename('metafile')

        # generated articles will be combined into epub file
        self.articles = []
        self.chapters = []

        # book basic information
        self.bookname = config.get_bookname()
        self.bookcname = config.get_bookcname()
        self.booktype = config.get_booktype()
        
        # book meta information
        self.bookid = config.get_book_meta('bookid')
        self.bookcat = config.get_book_meta('bookcat')
        self.author = config.get_book_meta('author')
        self.publisher = config.get_book_meta('publisher')
        self.covertitle = config.get_book_meta('covertitle')
        self.contentstitle = config.get_book_meta('contentstitle')
        self.fronttitle = config.get_book_meta('fronttitle')
        self.navtitle = config.get_book_meta('navtitle')

        # target epub directory
        self.target_rootdir = config.get_target_epub_dirname('root')
        self.target_epubdir = config.get_target_epub_dirname('epub')
        self.target_metainfdir = config.get_target_epub_dirname('metainf')
        self.target_xhtmldir = config.get_target_epub_dirname('xhtml')
        self.target_cssdir = config.get_target_epub_dirname('css')
        self.target_jsdir = config.get_target_epub_dirname('js')
        self.target_imgdir = config.get_target_epub_dirname('img')
        
        # some target epub resource filename
        self.target_coverpage = config.get_target_epub_filename('coverpage', False)
        self.target_frontpage = config.get_target_epub_filename('frontpage', False)
        self.target_contentspage = config.get_target_epub_filename('contentspage', False)
        self.target_navpage = config.get_target_epub_filename('navpage', False)
        self.target_packagefile = config.get_target_epub_filename('packagefile', False)
        self.target_ncxfile = config.get_target_epub_filename('ncxfile', False)
        self.target_maincssfile = config.get_target_epub_filename('maincssfile', False)
        self.target_coverfile = config.get_target_epub_filename('coverfile', False)

        # chapter&article id prefix in the contents
        self.article_id_prefix = config.get_prefix_of_article_in_contents()
        self.chapter_id_prefix = config.get_prefix_of_chapter_in_contents()
        
        # template directory
        self.templatedir = config.get_templatedir()
        # template manager
        self.tplmanager = TplSimpleManager(self.templatedir)

        self.generator = PageGenerator(self.target_xhtmldir, {
            'booktype': self.booktype,
            'navtitle': self.navtitle,
            'covertitle': self.covertitle,
            'fronttitle': self.fronttitle,
            'contentstitle': self.contentstitle,
            'navpage': self.target_navpage,
            'coverpage': self.target_coverpage,
            'frontpage': self.target_frontpage,
            'contentspage': self.target_contentspage,
            'maincssfile': self.target_maincssfile,
            'coverfile': self.target_coverfile,
            'article_id_prefix': self.article_id_prefix,
            'chapter_id_prefix': self.chapter_id_prefix
        })

        self.packager = PackageGenerator(self.target_epubdir, {
            'packagefile': self.target_packagefile,
            'ncxfile': self.target_ncxfile,
            'navpage': self.target_navpage,
            'coverpage': self.target_coverpage,
            'frontpage': self.target_frontpage,
            'contentspage': self.target_contentspage,
            'maincssfile': self.target_maincssfile,
            'coverfile': self.target_coverfile,
            'booktype': self.booktype,
            'bookid': self.bookid,
            'bookcname': self.bookcname,
            'author': self.author,
            'publisher': self.publisher
        })

    def run(self):
        self.generate_epub()
        self.generate_package()

    def generate_epub(self):
        self.generate_articles()
        self.generate_chapters()
        self.generate_coverpage()
        self.generate_frontpage()
        self.generate_contentspage()
        self.generate_navpage()

    def generate_package(self):
        self.packager.generate_opf(self.articles, self.chapters, self.tplmanager.get_template('opf'))
        self.packager.generate_ncx(self.articles, self.chapters, self.tplmanager.get_template('ncx'))

    def generate_articles(self):
        with open(self.jsonfile, 'r', encoding='utf-8') as f:
            for line in f:
                article = ArticleRaw(json.loads(line))
                self.generator.generate_article({
                    'id': article.get_id(),
                    'title': article.get_title(),
                    'body': article.get_body()
                }, self.tplmanager.get_template('article'))
                self.articles.append([article.get_id(), article.get_title()])
        self.articles = sorted(self.articles, key=lambda article: article[0])

    def generate_chapters(self):
        if self.isstandalone:
            return
        for chapterid in self.chapterid_list:
            chapter = ChapterRaw(self.config.get_chapter(chapterid))
            self.generator.generate_chapter({
                'id': chapter.get_id(),
                'title': chapter.get_title()
            }, self.tplmanager.get_template('chapter'))
            self.chapters.append([chapter.get_id(), chapter.get_title(), chapter.get_articles()])
        self.chapters = sorted(self.chapters, key=lambda chapter: chapter[0])
    
    def generate_coverpage(self):
        self.generator.generate_coverpage(self.tplmanager.get_template('cover'))

    def generate_frontpage(self):
        if self.booktype == 'tw':
            tpl = self.tplmanager.get_template('front_tw')
        else:
            tpl = self.tplmanager.get_template('front_zh')
        self.generator.generate_frontpage({
            'bookid': 'xxxxxxxx-xxxxxxxx',
            'bookcname': self.bookcname,
            'author': self.author,
            'publisher': self.publisher,
            'bookcat': self.bookcat,
            'publish_year': 'xxxx',
            'modify_year': 'xxxx',
            'modify_month': 'xx',
            'modify_day': 'xx'
        }, tpl)

    def generate_navpage(self):
        self.generator.generate_navpage(
            self.articles, 
            self.chapters, 
            self.tplmanager.get_template('nav')
        )

    def generate_contentspage(self):
        self.generator.generate_contentspage(
            self.articles, 
            self.chapters, 
            self.tplmanager.get_template('contents')
        )