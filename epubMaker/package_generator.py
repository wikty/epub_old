# -*- coding:utf-8 -*-
import os, time

class PackageGenerator():

    @staticmethod
    def now():
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(time.time()))

    @staticmethod
    def generate_opf(filename, title, author, publisher, bookid, coverfile, navpage, coverpage, frontpage, contentspage, ncxfile, articles):
        with open(filename, 'w', encoding='utf-8') as f:
            # package header, metadata
            f.write((PackageGenerator.OPF_HEADER).format(
                title=title, 
                author=author,
                publisher=publisher,
                bookid=bookid,
                datetime=PackageGenerator.now()
            ))

            # item, itemref
            items = []
            itemrefs = []
            items.append(PackageGenerator.OPF_XHTML_NAV_ITEM.format(filename=navpage, id='nav'))
            items.append(PackageGenerator.OPF_XHTML_NCX_ITEM.format(filename=ncxfile, id='ncx'))
            items.append(PackageGenerator.OPF_IMAGE_ITEM.format(filename=coverfile, id=coverfile))
            items.append(PackageGenerator.OPF_CSS_ITEM.format(filename='main.css', id='main.css'))
            items.append(PackageGenerator.OPF_XHTML_COVER_ITEM.format(filename=coverpage, id=coverpage))
            items.append(PackageGenerator.OPF_XHTML_ITEM.format(id=frontpage))
            items.append(PackageGenerator.OPF_XHTML_ITEM.format(id=contentspage))
            itemrefs.append(PackageGenerator.OPF_ITEMREF.format(id='nav', linear='no'))
            itemrefs.append(PackageGenerator.OPF_ITEMREF.format(id=coverpage, linear='yes'))
            itemrefs.append(PackageGenerator.OPF_ITEMREF.format(id=frontpage, linear='yes'))
            itemrefs.append(PackageGenerator.OPF_ITEMREF.format(id=contentspage, linear='yes'))
            for article in articles:
                items.append(PackageGenerator.OPF_XHTML_ITEM.format(id='.'.join([article['filename'], 'xhtml'])))
                itemrefs.append(PackageGenerator.OPF_ITEMREF.format(id='.'.join([article['filename'], 'xhtml']), linear='yes'))  

            #manifest
            f.write(PackageGenerator.OPF_MANIFEST.format(items=''.join(items)))
            # spine
            f.write(PackageGenerator.OPF_SPINE.format(itemrefs=''.join(itemrefs)))
            # package footer
            f.write(PackageGenerator.OPF_FOOTER)
    @staticmethod
    def generate_ncx(filename, bookcname, bookid, articles, covertitle, fronttitle, contentstitle):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(PackageGenerator.NCX_HEADER.format(bookid=bookid, title=bookcname))

            l = []
            for article in articles:
                l.append(PackageGenerator.NCX_NAVPOINT.format(id=article['article_id'], filename=article['filename'], title=article['title']))

            f.write('\n'.join(l))
            f.write(PackageGenerator.NCX_FOOTER)

    OPF_HEADER = \
"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" prefix="rendition: http://www.idpf.org/vocab/rendition/#" unique-identifier="book-id" version="3.0" xml:lang="en">
   <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:identifier id="book-id">{bookid}</dc:identifier>
      <dc:title>{title}</dc:title>
      <dc:creator>{author}</dc:creator>
      <dc:publisher>{publisher}</dc:publisher>
      <dc:language>zh-cn</dc:language>
      <meta property="dcterms:modified">{datetime}</meta>
      <meta property="rendition:layout">reflowable</meta>
      <meta property="rendition:orientation">auto</meta>
      <meta property="rendition:spread">auto</meta>
      <meta content="0.7.4" name="Sigil version" />
   </metadata>
"""

    OPF_FOOTER = \
"""
   <guide>
      <reference href="xhtml/coverpage.xhtml" type="cover" />
   </guide>
</package>"""

    OPF_MANIFEST = \
"""   <manifest>
{items}   </manifest>
"""

    OPF_IMAGE_ITEM = \
"""      <item href="img/{filename}" id="{id}" media-type="image/jpeg" />
"""

    OPF_CSS_ITEM = \
"""      <item href="css/{filename}" id="{id}" media-type="text/css" />
"""

    OPF_JS_ITEM = \
"""      <item href="js/{filename}" id="{id}" media-type="text/javascript" />
"""

    OPF_XHTML_ITEM = \
"""      <item href="xhtml/{id}" id="{id}" media-type="application/xhtml+xml" />
"""
   
    OPF_XHTML_NAV_ITEM = \
"""      <item href="xhtml/{filename}" id="{id}" media-type="application/xhtml+xml" properties="nav"/>
"""
    
    OPF_XHTML_COVER_ITEM = \
"""      <item href="xhtml/{filename}" id="{id}" media-type="application/xhtml+xml" properties="svg"/>
"""

    OPF_XHTML_NCX_ITEM = \
"""      <item href="{filename}" id="{id}" media-type="application/x-dtbncx+xml" />
"""

    OPF_SPINE = \
"""   <spine toc="ncx">
{itemrefs}   </spine>"""

    OPF_ITEMREF = \
"""      <itemref idref="{id}" linear="{linear}"/>
"""

    NCX_HEADER = \
"""<?xml version="1.0" encoding="UTF-8" standalone="no" ?><ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta content="{bookid}" name="dtb:uid"/>
    <meta content="1" name="dtb:depth"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
  <docTitle>
    <text>{title}</text>
  </docTitle>
  <navMap>"""

    NCX_FOOTER = \
"""
  </navMap>
</ncx>"""

    NCX_NAVPOINT = \
"""
    <navPoint id="navPoint-{id}" playOrder="{id}">
      <navLabel>
        <text>{title}</text>
      </navLabel>
      <content src="xhtml/{filename}.xhtml" />
    </navPoint>"""
