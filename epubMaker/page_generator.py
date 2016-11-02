# -*- coding:utf-8 -*-
class PageGenerator():
    @staticmethod
    def generate(filename, template, data):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template.format(**data))

    @staticmethod
    def generate_article(filename, article):
        PageGenerator.generate(filename, PageGenerator.ARTICLE_TEMPLATE, article)

    @staticmethod
    def generate_navpage(filename, data):
        PageGenerator.generate(filename, PageGenerator.NAV_TEMPLATE, data)

    @staticmethod
    def generate_coverpage(filename, data):
        with open(filename, 'w', encoding='utf-8') as f:
            content = PageGenerator.COVER_TEMPLATE
            for key in data:
                content = content.replace('{'+key+'}', data[key])
            f.write(content)

    @staticmethod
    def generate_frontpage(filename, data):
        content = ''
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            for key in data:
                content = content.replace('{'+key+'}', data[key])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def generate_contentspage(filename, data):
        PageGenerator.generate(filename, PageGenerator.CONTENTS_TEMPLATE, data)

    # @staticmethod
    # def generate_infopage(filename, **data):
    #     PageGenerator.generate(filename, PageGenerator.INFOPAGE_TEMPLATE, data)

    INDEX_TEMPLATE = \
"""<?xml version="1.0" encoding="utf-8"?>
<html xml:lang="zh-CN" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="provider" content="{provider}"/>
        <meta name="builder" content="{builder}"/>
        <meta name="right" content="{right}"/>
        {css}
        <title>{title}</title>
    </head>
    <body>
        <div>
          <h1>{title}</h1>
        </div>
        <hr />
        <br />
        <ol>
          {content}
        </ol>
    </body>
</html>"""

    INFOPAGE_TEMPLATE = \
"""<?xml version="1.0" encoding="utf-8"?>
<html xml:lang="zh-CN" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="provider" content="{provider}"/>
        <meta name="builder" content="{builder}"/>
        <meta name="right" content="{right}"/>
        {css}
        <title>{title}</title>
    </head>
    <body>
        <h1>{title}</h1>
        <div>
        {right}
        </div>
    </body>
</html>"""

    ARTICLE_TEMPLATE = \
"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:xml="http://www.w3.org/XML/1998/namespace" xmlns:epub="http://www.idpf.org/2007/ops" >
    <head>
        <meta charset="utf-8"/>
        <link href="../css/main.css" rel="stylesheet" type="text/css" />
        <title>{title}</title>
    </head>
    <body>
        <h2><a href="{contentspage}#{contents_id}">{title}</a></h2>
        {content}
    </body>
</html>"""

    NAV_TEMPLATE = \
"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<link href="../css/main.css" rel="stylesheet" type="text/css" />
<title>{title}</title>
</head>
<body>
<nav epub:type="toc" id="toc">
  <h2>{title}</h2>
  <ol epub:type="list">
    <li><a href="{coverpage}">{cover}</a></li>
    <li><a href="{frontpage}">{copyright}</a></li>
    <li><a href="{contents}">{contents}</a></li>
    {content}
  </ol>
</nav>
</body>
</html>"""

    COVER_TEMPLATE = \
"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops" >
    <head>
        <meta content="true" name="calibre:cover" />
        <title>封面</title>
        <style type="text/css">
            @page {padding: 0pt; margin:0pt}
            body { text-align: center; padding:0pt; margin: 0pt; }
        </style>
    </head>
    <body>
        <div>
            <svg xmlns="http://www.w3.org/2000/svg" height="100%" preserveAspectRatio="xMidYMid meet" version="1.1" viewBox="0 0 900 1380" width="100%" xmlns:xlink="http://www.w3.org/1999/xlink">
                <image height="1380" width="900" xlink:href="../img/{cover}"></image>
            </svg>
        </div>
    </body>
</html>"""

    CONTENTS_TEMPLATE = \
"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:xml="http://www.w3.org/XML/1998/namespace">
<head>
  <link href="../css/main.css" rel="stylesheet" type="text/css" />
  <title>{title}</title>
</head>

<body>
<div class="toc">
  <h2>{title}</h2>
  {content}
</div>
</body>
</html>"""