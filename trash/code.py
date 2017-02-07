 @staticmethod
    def generate(filename, template, data):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(template.format(**data))

    @staticmethod
    def generate_article(article):

        PageGenerator.generate(filename, PageGenerator.ARTICLE_TEMPLATE, article)

    @staticmethod
    def generate_navpage(filename, data):
        PageGenerator.generate(filename, PageGenerator.NAV_TEMPLATE, data)

    

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
        <h2><a href="{contentspage}#a{article_id}">{title}</a></h2>
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
    <li><a href="{coverpage}">{covertitle}</a></li>
    <li><a href="{frontpage}">{fronttitle}</a></li>
    <li><a href="{contentspage}">{contentstitle}</a></li>
{content}
  </ol>
</nav>
</body>
</html>"""

    COVER_TEMPLATE = \
"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:xml="http://www.w3.org/XML/1998/namespace" >
    <head>
        <meta content="true" name="calibre:cover" />
        <title>封面</title>
        <style type="text/css">
            @page {padding: 0pt; margin:0pt}
            body { text-align: center; padding:0pt; margin: 0pt; }
            .cover_img {
                margin-left: 0px;
                margin-right: 0px;
                margin-top: 0px;
                margin-bottom: 0px;
                text-align: center;
            }

            .cover_img img {
                height: 100%;
            }
        </style>
    </head>
    <body>
        <div class="cover_img">
            <img alt="cover image" src="../img/{cover}" />
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